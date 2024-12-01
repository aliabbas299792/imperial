// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.24;

import {IHumanResources} from "./IHumanResources.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ISwapRouter} from "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";
import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

contract HumanResources is IHumanResources {
    using SafeERC20 for IERC20;

    // Constants for contract addresses and configuration
    address private constant WETH = 0x4200000000000000000000000000000000000006;
    address private constant USDC = 0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85;
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
