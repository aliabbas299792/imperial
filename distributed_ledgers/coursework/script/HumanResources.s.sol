// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {HumanResources} from "@src/HumanResources.sol";

contract DeployScript is Script {
    function setUp() public {}

    event Deployed(address addr);

    function run() public {
        uint256 deployerKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerKey);

        HumanResources hr = new HumanResources(msg.sender);
        address deployedAddress = address(hr);

        console.log("Deployed at: ", deployedAddress);
        vm.stopBroadcast();
    }
}
