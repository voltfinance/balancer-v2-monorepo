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
    getUserSubscribedDistributionIdByIndex(address, address, uint256) returns (bytes32) envfree
    getUserSubscribedDistributionIndexById(address, address, bytes32) returns uint256 envfree

    // view functions
    isSubscribed(bytes32, address) returns bool envfree

    // non view functions
    createDistribution(address, address, uint256) returns bytes32
    getUserBalance(address, address) returns uint256 envfree
    subscribeDistributions(bytes32[])
    unsubscribeDistributions(bytes32[]) 
    stake(address, uint256, address, address)
    unstake(address, uint256, address, address)
    // isSubscribed(bytes32, address, address, bytes32[]) returns bool envfree
}

/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////    Definitions    /////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// Dist Not Exist - all parameters are set to default values.
definition distNotExist(bytes32 distId) returns bool = 
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
definition distNew(bytes32 distId) returns bool = 
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
        getLastUpdateTime(distId) != 0 && 
        (getTotalSupply(distId) == 0 ? getGlobalTokensPerStake(distId) == 0 : getGlobalTokensPerStake(distId) != 0);

// Dist Finished, not active - 4 non-zero parameters from distCreated + 4 more.
// payment rate is assumed to be non-zero once dist if funded. that means that the funder of the dist always make sure that amount > duration.
definition distFinished(bytes32 distId, env e) returns bool = 
        getStakingToken(distId) != 0 && 
        getDistributionToken(distId) != 0 &&
        getOwner(distId) != 0 &&
        getDuration(distId) != 0 &&
        (getPeriodFinish(distId) != 0 && getPeriodFinish(distId) < e.block.timestamp) &&
        getPaymentRate(distId) != 0 && 
        getLastUpdateTime(distId) == getPeriodFinish(distId); //&& 
        // this is not entierly corret. we should only care for token staked within the active period. This line is commented as globalTPS probably isn't important in this state
        // (getTotalSupply(distId) == 0 ? getGlobalTokensPerStake(distId) == 0 : getGlobalTokensPerStake(distId) != 0);

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Helpers    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

function helperFunctions(method f, env e, address stakingToken, address sender, bytes32 distributionId, bytes32[] distributionIds) {
        uint256 amount; address recipient;

        if (f.selector == subscribeDistributions(bytes32[]).selector) {
                subscribeDistributions(e, distributionIds);
        } else if (f.selector == unsubscribeDistributions(bytes32[]).selector) {
        	unsubscribeDistributions(e, distributionIds);
        } else if (f.selector == stake(address, uint256, address, address).selector) {
        	stake(e, stakingToken, amount, sender, recipient);
        } else {
                unstake(e, stakingToken, amount, sender, recipient);
        } 
}

function requireArrayCorrelation(address stakingToken, address user, uint256 index, bytes32 distId, bytes32[] distributionIdArray){
    require distributionIdArray[0] == distId;
    requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distId);
}

function requireEnvValuesNotZero(env e){
    require e.msg.sender != 0;
    require e.block.number != 0;
    require e.block.timestamp != 0;
}

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Invariants    /////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// V@V - The global reward token per stake token var is always greater or equal to the user's reward token per stake token 
invariant globalGreaterOrEqualUser(bytes32 distributionId, address stakingToken, address sender)
        getGlobalTokensPerStake(distributionId) >= getUserTokensPerStake(distributionId, stakingToken, sender)


// V@V - duration, owner, staking token and dist token are either initialized (!=0) or uninitialized (0) simultaneously
invariant distExistInitializedParams(bytes32 distId, env e)
        (getDuration(distId) == 0 <=> getOwner(distId) == 0) && 
        (getOwner(distId) == 0 <=> getStakingToken(distId) == 0) && 
        (getStakingToken(distId) == 0 <=> getDistributionToken(distId) == 0)
        {
            preserved with (env e2)
            { 
                require e.msg.sender == e2.msg.sender;
                require e2.msg.sender != 0;
            }
        }


// V@V - _indexes mapping and _values array are correlated in the enumerable set
invariant enumerableSetIsCorrelated(address stakingToken, address user, uint256 index, bytes32 distId)
       getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distId <=> getUserSubscribedDistributionIndexById(stakingToken, user, distId) == index
        {
            preserved unsubscribeDistributions(bytes32[] distributionIdArray) with (env e)
            {
                require distributionIdArray[0] == distId;
            }
        }


// V@V - A user cannot be subscribed to a distribution that does not exist
invariant notSubscribedToNonExistingDist(bytes32 distId, address user)
        getDuration(distId) == 0 => !isSubscribed(distId, user)
        {
            preserved unsubscribeDistributions(bytes32[] distributionIdArray) with (env e)
            {
                address stakingToken; uint256 index;
                requireArrayCorrelation(stakingToken, user, index, distId, distributionIdArray);
            }

        }


// F@F - fail on STAKE. If duration/owner/staking_token/distribution_token are not set, the distribution does not exist
invariant conditionsDistNotExist(bytes32 distId, address user)
        getDuration(distId) == 0 => distNotExist(distId)
        {
            preserved 
            {
                address stakingToken; uint256 index; bytes32[] distributionIdArray;
                // requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distId);
                // require distributionIdArray[0] == distId;
                requireArrayCorrelation(stakingToken, user, index, distId, distributionIdArray);
                requireInvariant notSubscribedToNonExistingDist(distId, user);
            }
        }


/* ask the balancer team about the payment rate = 0. if we assume, remove it from the inv */

// F@F - fail on FUND because amount<duration. lastUpdateTime, periodFinished and PaymentRate are either initialized (!=0) or uninitialized (0) simultaneously
// we assume here paymentRate != 0, although it is technically possible to have paymentRate == 0.
invariant distActivatedAtLeastOnceParams(bytes32 distId, env e)
        (getLastUpdateTime(distId) == 0 <=> getPeriodFinish(distId) == 0) //&& 
        // (getPeriodFinish(distId) == 0 <=> getPaymentRate(distId) == 0)
        {
            preserved with (env e2)
            {
                require e.block.timestamp == e2.block.timestamp;
                require e2.block.timestamp > 0;
            }
        }

// 1) duration != 0 => distNew XOR distActive XOR distFinished


// Creating a dist bringing us from the state distNotExist to distNew (no other function does that)
rule conditionsDistNew(bytes32 distId){
    method f; env e; calldataarg args;
    require distNotExist(distId);
    require e.msg.sender != 0;
    f(e,args);
    if (f.selector == createDistribution(address, address, uint256).selector){
        assert distNew(distId), "distribution is in another state"; 
    }
    else{
        assert distNotExist(distId), "distribution changed state without creating a distribution";
    }
}

/////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////    Rules    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

rule changesCheckOfUserTokenPerStake(method f) filtered { f -> f.selector == subscribeDistributions(bytes32[]).selector 
                                                                && f.selector == unsubscribeDistributions(bytes32[]).selector
                                                                && f.selector == stake(address, uint256, address, address).selector
                                                                && f.selector == unstake(address, uint256, address, address).selector}{
        env e;
        calldataarg args;

        bytes32 distributionId;

        bytes32[] distributionIds = [distributionId]; 

        address stakingToken; address sender;

        uint256 balanceBefore = getUserBalance(stakingToken, sender);
        uint256 utpsBefore = getUserTokensPerStake(distributionId, stakingToken, sender);

        helperFunctions(f, e, stakingToken, sender, distributionId, distributionIds);

        uint256 balanceAfter = getUserBalance(stakingToken, sender);
        uint256 utpsAfter = getUserTokensPerStake(distributionId, stakingToken, sender);

        assert utpsBefore < utpsAfter;
}

rule gtpsMonotonicity(bytes32 distributionId, method f){
        uint256 gtpsBefore = getGlobalTokensPerStake(distributionId);

        env e;
        calldataarg args;
        f(e, args);

        uint256 gtpsAfter = getGlobalTokensPerStake(distributionId);

        assert gtpsBefore <= gtpsAfter, "gtps was decreased";
}

rule utpsMonotonicity(bytes32 distributionId, method f){
        address stakingToken; 
        address sender;

        uint256 utpsBefore = getUserTokensPerStake(distributionId, stakingToken, sender);

        env e;
        calldataarg args;
        f(e, args);

        uint256 utpsAfter = getUserTokensPerStake(distributionId, stakingToken, sender);

        assert utpsBefore <= utpsAfter, "utps was decreased";
}
