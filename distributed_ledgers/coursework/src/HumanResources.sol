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

    // External contracts
    ISwapRouter private constant swapRouter =
        ISwapRouter(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    AggregatorV3Interface private constant ethUsdFeed =
        AggregatorV3Interface(0x13e3Ee699D1909E989722E753853AE30b17e08c5);

    address public immutable hrManager;

    constructor(address _hrManager) {
        require(_hrManager != address(0), "Invalid HR manager address");
        hrManager = _hrManager;
    }

    modifier onlyHrManager() {
        if (msg.sender != hrManager) revert NotAuthorized();
        _;
    }

    receive() external payable {}
}
