/// @notice This is a test contract for the HumanResources contract
/// You can either run this test for a contract deployed on a local fork or for a contract deployed on Optimism
/// To use a local fork, start `anvil` using `anvil --rpc-url $RPC_URL` where `RPC_URL` should point to an Optimism RPC.
/// Deploy your contract on the local fork and set the following environment variables:
/// - HR_CONTRACT: the address of the deployed contract
/// - ETH_RPC_URL: the RPC URL of the local fork (likely http://localhost:8545)
/// To run on Optimism, you will need to set the same environment variables, but with the address of the deployed contract on Optimism
/// and ETH_RPC_URL should point to the Optimism RPC.
/// Once the environment variables are set, you can run the tests using `forge test --mp test/HumanResourcesTests.t.sol`
/// assuming that you copied the file into the `test` folder of your project.

// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.24;

/// @notice You may need to change these import statements depending on your project structure and where you use this test
import {Test, stdStorage, StdStorage} from "forge-std/Test.sol";
import {HumanResources, IHumanResources} from "@src/HumanResources.sol";
import {PriceUtilities} from "@src/PriceUtilities.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {ISwapRouter} from "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";

contract HumanResourcesTest is PriceUtilities, Test {
    using stdStorage for StdStorage;

    HumanResources public humanResources;

    address public hrManager;
    address public alice = makeAddr("alice");
    address public bob = makeAddr("bob");

    uint256 public aliceSalary = 2100e18;
    uint256 public bobSalary = 700e18;

    // events to test against
    event EmployeeRegistered(address indexed employee, uint256 weeklyUsdSalary);
    event EmployeeTerminated(address indexed employee);
    event SalaryWithdrawn(address indexed employee, bool isEth, uint256 amount);
    event CurrencySwitched(address indexed employee, bool isEth);

    uint256 ethPrice;

    function setUp() public {
        vm.createSelectFork(vm.envString("ETH_RPC_URL"));
        humanResources = HumanResources(payable(vm.envAddress("HR_CONTRACT")));

        (, int256 answer, , , ) = ethUsdFeed.latestRoundData();
        uint256 feedDecimals = ethUsdFeed.decimals();
        ethPrice = uint256(answer) * 10 ** (18 - feedDecimals);
        hrManager = humanResources.hrManager();
    }

    function test_registerEmployee() public {
        _registerEmployee(alice, aliceSalary);
        assertEq(humanResources.getActiveEmployeeCount(), 1);

        uint256 currentTime = block.timestamp;

        (
            uint256 weeklySalary,
            uint256 employedSince,
            uint256 terminatedAt
        ) = humanResources.getEmployeeInfo(alice);
        assertEq(weeklySalary, aliceSalary);
        assertEq(employedSince, currentTime);
        assertEq(terminatedAt, 0);

        skip(10 hours);

        _registerEmployee(bob, bobSalary);

        (weeklySalary, employedSince, terminatedAt) = humanResources
            .getEmployeeInfo(bob);
        assertEq(humanResources.getActiveEmployeeCount(), 2);

        assertEq(weeklySalary, bobSalary);
        assertEq(employedSince, currentTime + 10 hours);
        assertEq(terminatedAt, 0);
    }

    function test_registerEmployee_twice() public {
        _registerEmployee(alice, aliceSalary);
        vm.expectRevert(IHumanResources.EmployeeAlreadyRegistered.selector);
        _registerEmployee(alice, aliceSalary);
    }

    function test_salaryAvailableUSDC() public {
        _registerEmployee(alice, aliceSalary);
        skip(2 days);
        assertEq(
            humanResources.salaryAvailable(alice),
            ((aliceSalary / 1e12) * 2) / 7
        );

        skip(5 days);
        assertEq(humanResources.salaryAvailable(alice), aliceSalary / 1e12);
    }

    function test_salaryAvailable_eth() public {
        _registerEmployee(alice, aliceSalary);
        uint256 expectedSalary = (aliceSalary * 1e18 * 2) / ethPrice / 7;
        vm.prank(alice);
        humanResources.switchCurrency();
        skip(2 days);
        assertApproxEqRel(
            humanResources.salaryAvailable(alice),
            expectedSalary,
            0.01e18
        );
        skip(5 days);
        expectedSalary = (aliceSalary * 1e18) / ethPrice;
        assertApproxEqRel(
            humanResources.salaryAvailable(alice),
            expectedSalary,
            0.01e18
        );
    }

    function test_withdrawSalaryUSDC() public {
        _mintTokensFor(USDC, address(humanResources), 10_000e6);
        _registerEmployee(alice, aliceSalary);
        skip(2 days);
        vm.prank(alice);
        humanResources.withdrawSalary();
        assertEq(
            IERC20(USDC).balanceOf(address(alice)),
            ((aliceSalary / 1e12) * 2) / 7
        );

        skip(5 days);
        vm.prank(alice);
        humanResources.withdrawSalary();
        assertEq(IERC20(USDC).balanceOf(address(alice)), aliceSalary / 1e12);
    }

    function test_withdrawSalary_eth() public {
        _mintTokensFor(USDC, address(humanResources), 10_000e6);
        _registerEmployee(alice, aliceSalary);
        uint256 expectedSalary = (aliceSalary * 1e18 * 2) / ethPrice / 7;
        vm.prank(alice);
        humanResources.switchCurrency();
        skip(2 days);
        vm.prank(alice);
        humanResources.withdrawSalary();
        assertApproxEqRel(alice.balance, expectedSalary, 0.01e18);
        skip(5 days);
        expectedSalary = (aliceSalary * 1e18) / ethPrice;
        vm.prank(alice);
        humanResources.withdrawSalary();
        assertApproxEqRel(alice.balance, expectedSalary, 0.01e18);
    }

    function test_reregisterEmployee() public {
        _mintTokensFor(USDC, address(humanResources), 10_000e6);
        _registerEmployee(alice, aliceSalary);
        skip(2 days);
        vm.prank(hrManager);
        humanResources.terminateEmployee(alice);
        skip(1 days);
        _registerEmployee(alice, aliceSalary * 2);

        skip(5 days);
        vm.prank(alice);
        humanResources.withdrawSalary();
        uint256 expectedSalary = ((aliceSalary * 2) / 7) +
            ((aliceSalary * 2 * 5) / 7);
        assertEq(
            IERC20(USDC).balanceOf(address(alice)),
            expectedSalary / 1e12
        );
    }

    //
    // --- Role Management Tests ---
    //

    function test_onlyHrManagerCanRegister() public {
        // test unauthorized registration attempt
        vm.prank(alice);
        vm.expectRevert(IHumanResources.NotAuthorized.selector);
        humanResources.registerEmployee(bob, bobSalary);
    }

    function test_onlyHrManagerCanTerminate() public {
        _registerEmployee(alice, aliceSalary);

        // test unauthorized termination attempt
        vm.prank(bob);
        vm.expectRevert(IHumanResources.NotAuthorized.selector);
        humanResources.terminateEmployee(alice);
    }

    function test_onlyEmployeeCanSwitchCurrency() public {
        // test non-employee attempt
        vm.prank(alice);
        vm.expectRevert(IHumanResources.NotAuthorized.selector);
        humanResources.switchCurrency();

        // register and terminate employee
        _registerEmployee(alice, aliceSalary);
        vm.prank(hrManager);
        humanResources.terminateEmployee(alice);

        // test terminated employee attempt
        vm.prank(alice);
        vm.expectRevert(IHumanResources.NotAuthorized.selector);
        humanResources.switchCurrency();
    }

    //
    // --- Registration and Termination Tests ---
    //

    function test_registration_emitsEvent() public {
        vm.expectEmit(true, true, true, true);
        emit EmployeeRegistered(alice, aliceSalary);
        _registerEmployee(alice, aliceSalary);
    }

    function test_termination_emitsEvent() public {
        _registerEmployee(alice, aliceSalary);

        vm.expectEmit(true, true, true, true);
        emit EmployeeTerminated(alice);
        vm.prank(hrManager);
        humanResources.terminateEmployee(alice);
    }

    function test_terminateEmployee_stopsAccrual() public {
        _registerEmployee(alice, aliceSalary);
        skip(2 days);

        vm.prank(hrManager);
        humanResources.terminateEmployee(alice);

        uint256 salaryAtTermination = humanResources.salaryAvailable(alice);
        skip(3 days);
        assertEq(humanResources.salaryAvailable(alice), salaryAtTermination);
    }

    //
    // --- Salary Calculation and Withdrawal Tests ---
    //

    function test_salaryAccrual_linearTime() public {
        _mintTokensFor(USDC, address(humanResources), 10_000e6);
        _registerEmployee(alice, aliceSalary);

        // test 1 day accrual
        skip(1 days);
        uint256 oneDaySalary = humanResources.salaryAvailable(alice);

        // reset and test 2 days accrual
        vm.prank(alice);
        humanResources.withdrawSalary();
        skip(2 days);
        uint256 twoDaysSalary = humanResources.salaryAvailable(alice);

        // two days should be exactly double one day since it's linear
        assertEq(twoDaysSalary, oneDaySalary * 2);
    }

    function test_switchCurrency_withdrawsFirst() public {
        _mintTokensFor(USDC, address(humanResources), 10_000e6);
        _registerEmployee(alice, aliceSalary);
        skip(2 days);

        uint256 expectedUsdc = humanResources.salaryAvailable(alice);
        vm.expectEmit(true, true, true, true);
        emit SalaryWithdrawn(alice, false, expectedUsdc);
        vm.expectEmit(true, true, true, true);
        emit CurrencySwitched(alice, true);

        vm.prank(alice);
        humanResources.switchCurrency();
    }

    function test_reregistration_currencyPreference() public {
        _mintTokensFor(USDC, address(humanResources), 10_000e6); // Add this line
        _registerEmployee(alice, aliceSalary);

        // switch to eth
        vm.prank(alice);
        humanResources.switchCurrency();

        // terminate and re-register
        vm.prank(hrManager);
        humanResources.terminateEmployee(alice);
        _registerEmployee(alice, aliceSalary);

        // verify preference reset to usdc
        skip(1 days);
        uint256 available = humanResources.salaryAvailable(alice);
        vm.prank(alice);
        humanResources.withdrawSalary();
        assertEq(IERC20(USDC).balanceOf(alice), available);
    }

    //
    // --- View Function Tests ---
    //

    function test_getEmployeeInfo_nonexistentEmployee() public {
        (uint256 salary, uint256 since, uint256 terminated) = humanResources
            .getEmployeeInfo(address(0xdead));
        assertEq(salary, 0);
        assertEq(since, 0);
        assertEq(terminated, 0);
    }

    function test_activeEmployeeCount() public {
        assertEq(humanResources.getActiveEmployeeCount(), 0);

        // register multiple employees
        _registerEmployee(alice, aliceSalary);
        _registerEmployee(bob, bobSalary);
        assertEq(humanResources.getActiveEmployeeCount(), 2);

        // terminate one
        vm.prank(hrManager);
        humanResources.terminateEmployee(bob);
        assertEq(humanResources.getActiveEmployeeCount(), 1);

        // re-register terminated employee
        _registerEmployee(bob, bobSalary);
        assertEq(humanResources.getActiveEmployeeCount(), 2);
    }

    function test_withdrawSalary_slippageProtection_atLimit() public {
        _mintTokensFor(USDC, address(humanResources), 10_000e6);
        _registerEmployee(alice, 1000e18);

        vm.prank(alice);
        humanResources.switchCurrency();
        skip(7 days);

        uint256 salaryInEth = humanResources.salaryAvailable(alice);
        _mintTokensFor(WETH, address(humanResources), salaryInEth);
        vm.deal(address(humanResources), salaryInEth);

        (, int256 answer, , , ) = ethUsdFeed.latestRoundData();
        uint256 usdcAmount = _convertToUsdcDecimals(salaryInEth * uint256(answer));
        uint256 maxAllowedAmount = _accountForSlippage(usdcAmount);

        vm.mockCall(
            address(swapRouter),
            abi.encodeWithSelector(ISwapRouter.exactOutputSingle.selector),
            abi.encode(maxAllowedAmount)
        );

        vm.prank(alice);
        humanResources.withdrawSalary(); // should not revert at 102%
    }

    function test_withdrawSalary_slippageProtection_aboveLimit() public {
        _mintTokensFor(USDC, address(humanResources), 10_000e6);
        _registerEmployee(alice, 1000e18);

        vm.prank(alice);
        humanResources.switchCurrency();
        skip(7 days);

        uint256 salaryInEth = humanResources.salaryAvailable(alice);
        _mintTokensFor(WETH, address(humanResources), salaryInEth);
        vm.deal(address(humanResources), salaryInEth);

        (, int256 answer, , , ) = ethUsdFeed.latestRoundData();
        uint256 usdcAmount = _convertToUsdcDecimals(salaryInEth * uint256(answer));

        // 103% slippage
        uint256 excessiveAmount = (usdcAmount * 103) / 100;

        vm.mockCall(
            address(swapRouter),
            abi.encodeWithSelector(ISwapRouter.exactOutputSingle.selector),
            abi.encode(excessiveAmount)
        );

        vm.expectRevert("Excessive slippage");
        vm.prank(alice);
        humanResources.withdrawSalary();
    }

    function _registerEmployee(address employeeAddress, uint256 salary) public {
        vm.prank(hrManager);
        humanResources.registerEmployee(employeeAddress, salary);
    }

    function _mintTokensFor(
        address token_,
        address account_,
        uint256 amount_
    ) internal {
        stdstore
            .target(token_)
            .sig(IERC20(token_).balanceOf.selector)
            .with_key(account_)
            .checked_write(amount_);
    }
}
