// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {HumanResources} from "@src/HumanResources.sol";

contract CounterScript is Script {
    HumanResources public counter;

    function setUp() public {}

    function run() public {
        uint256 deployerKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerKey);
        counter = new HumanResources(msg.sender);

        console.log("Deployed at: ", address(counter));
        vm.stopBroadcast();
    }
}
