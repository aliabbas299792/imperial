# Principles of Distributed Ledgers Coursework
This repository contains the 70017 Smart Contracts coursework, related to the management of employees and paying them.

## Documentation
### Overview
The contract implements a HR payment system that allows for employee registration, salary management, and payment in either USDC or ETH.
The contract integrates with Chainlink price feeds for ETH/USD pricing and Uniswap V3 for USDC/ETH swaps.
### .env
Copy `.env.example` to `.env` and fill in the values appropriately to be able to use the scripts in `utils/` properly/deploy the contract properly.

### Utilities
The `utils/` directory contains a variety of simple scripts for common `forge` operations.
- In particular, `local_deploy.sh` is very useful for testing, and substituting in the correct addresss in `.env`

### Interface Implementation

#### HR Manager Functions

##### `registerEmployee(address employee, uint256 weeklyUsdSalary)`
- Registers a new employee/reregisters a terminated employee
- Validates employee address and checks for existing active registration
- Stores employee information including salary (scaled to 18 decimals)
- Preserves any accumulated salary from previous termination
- Updates active employee count
- Emits `EmployeeRegistered` event

##### `terminateEmployee(address employee)`
- Terminates an active employee's contract
- Calculates and stores final salary owed up to termination
- Decrements active employee count
- Preserves withdrawable salary
- Emits `EmployeeTerminated` event

#### Employee Functions

##### `withdrawSalary()`
- Calculates available salary based on time elapsed and previous withdrawals
- Handles both active and terminated employee withdrawals
- Converts and transfers salary in preferred currency (USDC or ETH)
- Uses reentrancy guard for security
- Updates withdrawal timestamp and clears accumulated balance
- Emits `SalaryWithdrawn` event

##### `switchCurrency()`
- Toggles between USDC and ETH salary preference
- Automatically withdraws any available salary in current currency before switching
- Only callable by active employees
- Emits both `SalaryWithdrawn` and `CurrencySwitched` events

#### View Functions

##### `salaryAvailable(address employee)`
- Calculates total available salary including:
  - Current period accrual
  - Previously accumulated amount
- Returns amount in employee's preferred currency with appropriate decimals

##### `hrManager()`
- Returns the immutable HR manager address set at deployment

##### `getActiveEmployeeCount()`
- Returns current count of non-terminated employees

##### `getEmployeeInfo(address employee)`
- Returns employee's weekly salary, employment start date, and termination date
- Returns zeros for non-existent employees

### External Integrations

#### Chainlink Oracle Integration
- Uses ETH/USD price feed at `0x13e3Ee699D1909E989722E753853AE30b17e08c5`
- The price is used for converting between USD and ETH amounts
- Ensures accurate and manipulation-resistant price data
- Implements decimal scaling for price feed values

#### Uniswap V3 AMM Integration
- Swap Router at `0xE592427A0AEce92De3Edee1F18E0157C05861564`
- Implements exact output swaps for USDC to ETH conversion
- 2% slippage protection
- Uses 0.3% fee tier pool
- Handles WETH (un)wrapping for ETH payments

### Constants
- USDC: `0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85`
- WETH: `0x4200000000000000000000000000000000000006`
- Week duration: 7 days
- Slippage threshold: 2%
