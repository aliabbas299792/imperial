// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.24;

import {ISwapRouter} from "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";
import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

contract PriceUtilities {
    uint256 private constant USDC_DECIMALS = 6;
    uint256 private constant ETH_DECIMALS = 18;
    uint256 private constant SLIPPAGE_THRESHOLD = 102;

    // Constants for contract addresses and configuration
    address internal constant WETH = 0x4200000000000000000000000000000000000006;
    address internal constant USDC = 0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85;

    // External contracts
    ISwapRouter internal constant swapRouter =
        ISwapRouter(0xE592427A0AEce92De3Edee1F18E0157C05861564);
    AggregatorV3Interface internal constant ethUsdFeed =
        AggregatorV3Interface(0x13e3Ee699D1909E989722E753853AE30b17e08c5);


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
}
