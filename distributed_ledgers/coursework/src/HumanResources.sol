// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.24;

import {IHumanResources} from "./IHumanResources.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ISwapRouter} from "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";
import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

// used to protect against reentrancy attacks
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

interface IWETH is IERC20 {
    function withdraw(uint256) external;
}

contract HumanResources is IHumanResources, ReentrancyGuard {
    using SafeERC20 for IERC20;

    // Constants for contract addresses and configuration
    address private constant WETH = 0x4200000000000000000000000000000000000006;
    address private constant USDC = 0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85;
    uint24 private constant POOL_FEE = 3000;
    uint256 private constant WEEK = 7 days;
    uint256 private constant USDC_DECIMALS = 6;
    uint256 private constant ETH_DECIMALS = 18;
    uint256 private constant SLIPPAGE_THRESHOLD = 102; // 2% maximum slippage

    // External contracts
    ISwapRouter private constant swapRouter =
        ISwapRouter(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    AggregatorV3Interface private constant ethUsdFeed =
        AggregatorV3Interface(0x13e3Ee699D1909E989722E753853AE30b17e08c5);

    address public immutable hrManager;

    struct Employee {
        uint256 weeklyUsdSalary;
        uint256 employedSince;
        uint256 terminatedAt;
        uint256 lastWithdrawal;
        bool prefersEth;
        uint256 accumulatedSalaryBeforeTermination;
    }

    mapping(address => Employee) private employees;
    uint256 private activeEmployeeCount;

    constructor(address _hrManager) {
        require(_hrManager != address(0), "Invalid HR manager address");
        hrManager = _hrManager;
    }

    modifier onlyHrManager() {
        if (msg.sender != hrManager) revert NotAuthorized();
        _;
    }

    modifier onlyEmployee() {
        if (employees[msg.sender].employedSince == 0) revert NotAuthorized();
        _;
    }

    modifier onlyActiveEmployee() {
        // used to distinguish between functions that current and terminated
        // employees can call
        if (
            employees[msg.sender].employedSince == 0 ||
            (employees[msg.sender].terminatedAt != 0 &&
                employees[msg.sender].terminatedAt <= block.timestamp)
        ) {
            revert NotAuthorized();
        }
        _;
    }

    function withdrawSalary() external nonReentrant onlyEmployee {
        Employee storage employee = employees[msg.sender];
        uint256 amount = _calculateAvailableSalary(msg.sender);
        if (amount == 0) return;

        employee.lastWithdrawal = block.timestamp;
        employee.accumulatedSalaryBeforeTermination = 0;

        if (employee.prefersEth) {
            _withdrawEth(amount);
        } else {
            _withdrawUsdc(amount);
        }
    }

    function switchCurrency() external nonReentrant onlyActiveEmployee {
        Employee storage employee = employees[msg.sender];

        uint256 amount = _calculateAvailableSalary(msg.sender);
        if (amount > 0) {
            employee.lastWithdrawal = block.timestamp;
            employee.accumulatedSalaryBeforeTermination = 0;
            if (employee.prefersEth) {
                _withdrawEth(amount);
            } else {
                _withdrawUsdc(amount);
            }
        }

        employee.prefersEth = !employee.prefersEth;
        emit CurrencySwitched(msg.sender, employee.prefersEth);
    }
    function _withdrawUsdc(uint256 amount) internal {
        IERC20(USDC).safeTransfer(msg.sender, amount);
        emit SalaryWithdrawn(msg.sender, false, amount);
    }

    function _withdrawEth(uint256 amount) internal {
        uint256 usdcAmount = _calculateUsdcForEth(amount);

        IERC20 usdc = IERC20(USDC);
        usdc.approve(address(swapRouter), 0);
        usdc.approve(address(swapRouter), usdcAmount);

        ISwapRouter.ExactOutputSingleParams memory params = ISwapRouter
            .ExactOutputSingleParams({
                tokenIn: USDC,
                tokenOut: WETH,
                fee: POOL_FEE,
                recipient: address(this),
                deadline: block.timestamp,
                amountOut: amount,
                amountInMaximum: usdcAmount,
                sqrtPriceLimitX96: 0
            });

        // usdcAmount is the upper limit of how much we're
        // willing to pay for this amount of WETH, so if
        // the amountIn is greater than this, the transaction
        // will revert
        uint256 amountIn = swapRouter.exactOutputSingle(params);
        require(amountIn <= usdcAmount, "Excessive slippage");

        // make sure have enough weth before withdrawing
        require(
            IWETH(WETH).balanceOf(address(this)) >= amount,
            "Insufficient WETH"
        );

        IWETH(WETH).withdraw(amount);

        // attempt to transfer eth to employee/sender account
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "ETH transfer failed");

        emit SalaryWithdrawn(msg.sender, true, amount);
    }

    function _calculateUsdcForEth(
        uint256 ethAmount
    ) internal view returns (uint256) {
        (, int256 ethPrice, , , ) = ethUsdFeed.latestRoundData();
        require(ethPrice > 0, "Invalid ETH price");
        uint256 usdcAmount = _convertToUsdcDecimals(
            _accountForSlippage(ethAmount * uint256(ethPrice))
        );

        return usdcAmount;
    }

    function terminateEmployee(address employee) external onlyHrManager {
        Employee storage emp = employees[employee];
        if (emp.employedSince == 0 || emp.terminatedAt != 0) {
            revert EmployeeNotRegistered();
        }

        uint256 timeElapsed = block.timestamp - emp.lastWithdrawal;
        uint256 salaryUntilTermination = (emp.weeklyUsdSalary * timeElapsed) /
            WEEK;

        salaryUntilTermination += emp.accumulatedSalaryBeforeTermination;
        salaryUntilTermination = _convertToUsdcDecimals(salaryUntilTermination);

        emp.terminatedAt = block.timestamp;
        emp.accumulatedSalaryBeforeTermination = salaryUntilTermination;
        activeEmployeeCount--;

        emit EmployeeTerminated(employee);
    }

    function registerEmployee(
        address employee,
        uint256 weeklyUsdSalary
    ) external onlyHrManager {
        require(employee != address(0), "Invalid employee address");
        if (
            employees[employee].employedSince != 0 &&
            (employees[employee].terminatedAt == 0 ||
                employees[employee].terminatedAt > block.timestamp)
        ) {
            revert EmployeeAlreadyRegistered();
        }

        uint256 accumulatedSalary = employees[employee]
            .accumulatedSalaryBeforeTermination;

        employees[employee] = Employee({
            weeklyUsdSalary: weeklyUsdSalary,
            employedSince: block.timestamp,
            terminatedAt: 0,
            lastWithdrawal: block.timestamp,
            prefersEth: false,
            accumulatedSalaryBeforeTermination: accumulatedSalary
        });

        activeEmployeeCount++;
        emit EmployeeRegistered(employee, weeklyUsdSalary);
    }

    function _calculateAvailableSalary(
        address employeeAddress
    ) internal view returns (uint256) {
        Employee memory employee = employees[employeeAddress];
        if (employee.employedSince == 0) return 0;

        uint256 endTime = employee.terminatedAt == 0
            ? block.timestamp
            : employee.terminatedAt;

        uint256 timeElapsed = 0;
        if (endTime > employee.lastWithdrawal) {
            timeElapsed = endTime - employee.lastWithdrawal;
        }

        // current period salary in 18 decimals
        uint256 currentPeriodSalary = (employee.weeklyUsdSalary * timeElapsed) /
            WEEK;

        // total currency amount is current period plus accumulated
        uint256 totalAmount;
        if (employee.prefersEth) {
            // need to scale the accumulated amount back to 18 decimals
            totalAmount =
                currentPeriodSalary +
                _convertFromUsdcDecimals(
                    employee.accumulatedSalaryBeforeTermination
                );
        } else {
            // current period to usdc decimals and add accumulated
            totalAmount =
                _convertToUsdcDecimals(currentPeriodSalary) +
                employee.accumulatedSalaryBeforeTermination;
        }

        if (employee.prefersEth) {
            (, int256 ethPrice, , , ) = ethUsdFeed.latestRoundData();
            require(ethPrice > 0, "Invalid ETH price");

            // totalAmount in 18 decimals (USD)
            // ethPrice is in 8 decimals
            // want eth in 18 decimals
            return (totalAmount * 1e18) / (uint256(ethPrice) * 1e10);
        } else {
            return totalAmount;
        }
    }

    function _convertToUsdcDecimals(
        uint256 amount
    ) internal pure returns (uint256) {
        return amount / (10 ** (ETH_DECIMALS - USDC_DECIMALS));
    }

    function _convertFromUsdcDecimals(
        uint256 amount
    ) internal pure returns (uint256) {
        return amount * (10 ** (ETH_DECIMALS - USDC_DECIMALS));
    }

    function _accountForSlippage(
        uint256 amount
    ) internal pure returns (uint256) {
        return (amount * SLIPPAGE_THRESHOLD) / 100;
    }

    receive() external payable {}
}
