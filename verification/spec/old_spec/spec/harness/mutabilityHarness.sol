pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "./simplifiedVaultHarness.sol";

contract mutabilityHarness is simplifiedVaultHarness {
    /*
    This harness is used solely for the queryBatchSwapIsView rule.
    We isolate this rule because getStorageBytes32 ruins the storage analysis for the other methods examined.
    */
    using BalanceAllocation for bytes32;

    constructor(IAuthorizer authorizer) simplifiedVaultHarness(authorizer) {}

    function getStorageBytes32(bytes32 position) public view returns (bytes32 data) {
        assembly { 
            data := sload(position) 
        }
    }
}