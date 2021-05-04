pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "../../contracts/pools/weighted/WeightedPool2Tokens.sol";

contract WeightedPool2TokensHarness is WeightedPool2Tokens {
    constructor(NewPoolParams memory params) WeightedPool2Tokens(params) {} 

    function Harness_updateOracle(uint256 lastChangeBlock,
        uint256 balanceToken0,
        uint256 balanceToken1
    ) public {
        _updateOracle(lastChangeBlock, balanceToken0, balanceToken1);
    }

    function normalizedWeight1() public view returns (uint256) {
        return _normalizedWeights(true);
    }
    
    function normalizedWeight2() public view returns (uint256) {
        return _normalizedWeights(false);
    }
}