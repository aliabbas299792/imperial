// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {HumanResources} from "@src/HumanResources.sol";

interface ISubmit {
    function submit(address contractAddress) external;
}

contract DeployScript is Script {
    event Deployed(address addr);
    event Submitted(address addr);

    address constant SUBMISSION_CONTRACT =
        address(0xBE41D42E2D1373120B24dD27a5465d8eF48B9d34);

    function setUp() public {}

    function run() public {
        uint256 deployerKey = vm.envUint("PRIVATE_KEY");
        vm.startBroadcast(deployerKey);

        HumanResources hr = new HumanResources(vm.addr(deployerKey));
        address deployedAddress = address(hr);
        emit Deployed(deployedAddress);
        console.log("Deployed at: ", deployedAddress);

        ISubmit submissionContract = ISubmit(SUBMISSION_CONTRACT);
        submissionContract.submit(deployedAddress);
        emit Submitted(deployedAddress);
        console.log("Submitted to: ", SUBMISSION_CONTRACT);

        vm.stopBroadcast();
    }
}
