methods {
    getGlobalTokensPerStake(bytes32) returns uint256
    getUserTokensPerStake(bytes32, address, address) returns uint256
}

invariant globalGreaterOrEqualUser(bytes32 distributionId, address stakingToken, address sender, env e)
        getGlobalTokensPerStake(e, distributionId) >= getUserTokensPerStake(e, distributionId, stakingToken, sender)