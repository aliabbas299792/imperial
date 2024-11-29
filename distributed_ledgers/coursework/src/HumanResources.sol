// SPDX-License-Identifier: GPL-3.0
pragma solidity ^0.8.24;

import {IHumanResources} from "./IHumanResources.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {ISwapRouter} from "@uniswap/v3-periphery/contracts/interfaces/ISwapRouter.sol";
import {AggregatorV3Interface} from "@chainlink/contracts/src/v0.8/shared/interfaces/AggregatorV3Interface.sol";

contract HumanResources is IHumanResources {
    using SafeERC20 for IERC20;

    receive() external payable {}
}
