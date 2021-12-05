methods {    
    //getters for specific distribution
    getStakingToken(bytes32) returns address /*IERC20*/ envfree
    getDistributionToken(bytes32) returns address /*IERC20*/ envfree
    getOwner(bytes32) returns address envfree
    getTotalSupply(bytes32) returns uint256 envfree
    getDuration(bytes32) returns uint256 envfree
    getPeriodFinish(bytes32) returns uint256 envfree
    getPaymentRate(bytes32) returns uint256 envfree    
    getLastUpdateTime(bytes32) returns uint256 envfree
    getGlobalTokensPerStake(bytes32) returns uint256 envfree
    
    // getters for user staking
    getUserTokensPerStake(bytes32, address, address) returns uint256 envfree
}

/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////    Definitions    /////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// Dist Not Exist - all parameters are set to default values.
definition distNotCreated(bytes32 distId) returns bool = 
        getStakingToken(distId) == 0 &&
        getDistributionToken(distId) == 0 &&
        getOwner(distId) == 0 &&
        getTotalSupply(distId) == 0 &&
        getDuration(distId) == 0 &&
        getPeriodFinish(distId) == 0 &&
        getPaymentRate(distId) == 0 &&
        getLastUpdateTime(distId) == 0 &&
        getGlobalTokensPerStake(distId) == 0;

// Dist Created, but yet to be funded - 4 parameters are non-zero.
definition distCreated(bytes32 distId) returns bool = 
        getStakingToken(distId) != 0 && 
        getDistributionToken(distId) != 0 && 
        getOwner(distId) != 0 &&
        getDuration(distId) != 0 && 
        getPeriodFinish(distId) == 0 &&
        getPaymentRate(distId) == 0 && 
        getLastUpdateTime(distId) == 0 && 
        getGlobalTokensPerStake(distId) == 0;

// Dist Funded, hence active - 4 non-zero parameters from distCreated + 4 more.
// payment rate is assumed to be non-zero once dist if funded. that means that the funder of the dist always make sure that amount > duration.
definition distActive(bytes32 distId, env e) returns bool = 
        getStakingToken(distId) != 0 && 
        getDistributionToken(distId) != 0 &&
        getOwner(distId) != 0 &&
        getDuration(distId) != 0 &&
        (getPeriodFinish(distId) != 0 && getPeriodFinish(distId) >= e.block.timestamp) &&
        getPaymentRate(distId) != 0 && 
        getLastUpdateTime(distId) != 0;
        //(to_int256(getGlobalTokensPerStake(distId) == 0 && getTotalSupply(distId) == 0) xor to_int256(getGlobalTokensPerStake(distId) != 0 && getTotalSupply(distId) != 0));

// Dist Finished, not active - 4 non-zero parameters from distCreated + 4 more.
// payment rate is assumed to be non-zero once dist if funded. that means that the funder of the dist always make sure that amount > duration.
definition distInactive(bytes32 distId, env e) returns bool = 
        getStakingToken(distId) != 0 && 
        getDistributionToken(distId) != 0 &&
        getOwner(distId) != 0 &&
        getDuration(distId) != 0 &&
        (getPeriodFinish(distId) != 0 && getPeriodFinish(distId) < e.block.timestamp) &&
        getPaymentRate(distId) != 0 && 
        getLastUpdateTime(distId) == getPeriodFinish(distId); //&& 
        // (to_uint((getGlobalTokensPerStake(distId) == 0 && getTotalSupply(distId) == 0)) xor to_uint((getGlobalTokensPerStake(distId) != 0 && getTotalSupply(distId) != 0)));


// dist.duration == 0 => distNotCreated
// duration != 0 => 

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Invariants    /////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

invariant globalGreaterOrEqualUser(bytes32 distributionId, address stakingToken, address sender)
        getGlobalTokensPerStake(distributionId) >= getUserTokensPerStake(distributionId, stakingToken, sender)

/////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////    Rules    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

