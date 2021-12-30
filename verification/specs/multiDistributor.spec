using SymbolicVault as Vault

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
    getUserSubscribedDistributionIdByIndex(address, address, uint256) returns bytes32 envfree
    getUserSubscribedDistributionIndexById(address, address, bytes32) returns uint256 envfree
    getDistIdContainedInUserSubscribedDistribution(address, address, bytes32) returns bool envfree
    getUserBalance(address, address) returns uint256 envfree
    getUserSetLength(address, address) returns uint256 envfree

    // view functions
    isSubscribed(bytes32, address) returns bool envfree
    getDistributionId(address stakingToken, address distributionToken, address owner) returns bytes32 envfree => uniqueHashGhost(stakingToken, distributionToken, owner)


    // non view functions
    createDistribution(address, address, uint256) returns bytes32
    setDistributionDuration(bytes32, uint256)
    fundDistribution(bytes32, uint256)
    subscribeDistributions(bytes32[])
    unsubscribeDistributions(bytes32[]) 
    stake(address, uint256, address, address)
    stakeUsingVault(address, uint256, address, address)
    stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32)
    unstake(address, uint256, address, address)
    claim(bytes32[], bool, address, address)
    claimWithCallback(bytes32[], address, address, bytes)
    exit(address[], bytes32[])
    exitWithCallback(address[], bytes32[], address, bytes)

    // getters for harness
    _lastTimePaymentApplicableHarness(bytes32) returns uint256

    totalAssetsOfUser(address, address) returns uint256 => DISPATCHER(true)
    manageUserBalance((uint8,address,uint256,address,address)[]) => DISPATCHER(true)
    balanceOf(address) returns uint256 => DISPATCHER(true)
    transfer(address, uint256) returns bool => DISPATCHER(true)
    transferFrom(address, address, uint256) returns bool => DISPATCHER(true)
    getBalanceOf(address, address) returns uint256 => DISPATCHER(true)
    approve(address, uint256) returns (bool) => DISPATCHER(true)
    
    getUserUnclaimedTokensOfDistribution(bytes32, address, address) returns uint256
    getClaimableTokens(bytes32, address) returns uint256

    distributorCallback(bytes) => NONDET
    permit(address, address, uint256, uint256, uint8, bytes32, bytes32) => NONDET
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
definition distActive(bytes32 distId, env e) returns bool = 
        getStakingToken(distId) != 0 && 
        getDistributionToken(distId) != 0 &&
        getOwner(distId) != 0 &&
        getDuration(distId) != 0 &&
        (getPeriodFinish(distId) != 0 && getPeriodFinish(distId) >= e.block.timestamp) &&
        // getPaymentRate(distId) != 0 && 
        (getLastUpdateTime(distId) != 0 && getLastUpdateTime(distId) <= getPeriodFinish(distId)); //&&
        // if everybody stake then unstake at some point GTPS, total supply can be 0, yet GTPS != 0
        // if at least 1 user is staked and subscribe then GTPS != 0
        // (getTotalSupply(distId) == 0 ? getGlobalTokensPerStake(distId) == 0 : getGlobalTokensPerStake(distId) != 0);

// Dist Finished, not active - 4 non-zero parameters from distCreated + 4 more.
definition distFinished(bytes32 distId, env e) returns bool = 
        getStakingToken(distId) != 0 && 
        getDistributionToken(distId) != 0 &&
        getOwner(distId) != 0 &&
        getDuration(distId) != 0 &&
        (getPeriodFinish(distId) != 0 && getPeriodFinish(distId) < e.block.timestamp) &&
        // getPaymentRate(distId) != 0 &&
        (getLastUpdateTime(distId) != 0 && getLastUpdateTime(distId) <= getPeriodFinish(distId)); //&& 
        // this is not entierly corret. we should only care for token staked within the active period. This line is commented as globalTPS probably isn't important in this state
        // (getTotalSupply(distId) == 0 ? getGlobalTokensPerStake(distId) == 0 : getGlobalTokensPerStake(distId) != 0);

// Collection of functions that are not distribution specific - they may effect distIds that arent passed to the (mainly by staking/unstaking)
definition nonSpecificDistribution(method f) returns bool = 
    f.selector == stake(address, uint256, address, address).selector || 
    f.selector == stakeUsingVault(address, uint256, address, address).selector || 
    f.selector == stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32).selector || 
    f.selector == unstake(address, uint256, address, address).selector || 
    f.selector == exit(address[], bytes32[]).selector || 
    f.selector == exitWithCallback(address[], bytes32[], address, bytes).selector;

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Ghost    //////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// Ghost that keeps track of the hashing to assume determinism of the hashing operation.
ghost uniqueHashGhost(address, address, address) returns bytes32;


/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Helpers    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// Making sure the env does not take any 0 values which aren't realistic anyway
function requireEnvValuesNotZero(env e){
    require e.msg.sender != 0;
    require e.block.number != 0;
    require e.block.timestamp != 0;
}

/*
function callCreateDistributionWithSpecificDistId(method f, env e, bytes32 distId){
    address _stakingToken; address _distributionToken; uint256 _duration;
    if (f.selector == createDistribution(address, address, uint256).selector) {
        bytes32 distributionId = createDistribution(e, _stakingToken, _distributionToken, _duration);
        require distributionId == distId;
    } else {
        calldataarg args;
        f(e, args);
    }
}
*/

// Helper function for calling fundDistribution with specifica distId, and all other functions with arbitrary values
function callFundDistributionWithSpecificDistId(method f, env e, bytes32 distId){
    uint256 _amount;
    if (f.selector == fundDistribution(bytes32, uint256).selector) {
        fundDistribution(e, distId, _amount);
    } else {
        calldataarg args;
        f(e, args);
    }
}

// Calling all non-view function with specified parameters.
// A helper function that allows modification of the input args to assure specific values are being passed to the contract's functions when needed
function callAllFunctionsWithParameters(method f, env e, bytes32 distributionId, bytes32[] distributionIds, address stakingToken, address recipient){
    address distributionToken; uint256 duration; uint256 amount;
    address sender; uint256 deadline; uint8 v; bytes32 r; bytes32 s;
    bool toInternalBalance; address callbackContract; bytes callbackData; address[] stakingTokens;

	if (f.selector == createDistribution(address, address, uint256).selector) {
        bytes32 distId = createDistribution(e, stakingToken, distributionToken, duration);
        require distId == distributionId;
	} else if (f.selector == setDistributionDuration(bytes32, uint256).selector) {
        setDistributionDuration(e, distributionId, duration);
	} else if (f.selector == fundDistribution(bytes32, uint256).selector) {
		fundDistribution(e, distributionId, amount);
	} else if (f.selector == subscribeDistributions(bytes32[]).selector) {
        subscribeDistributions(e, distributionIds);
	} else if (f.selector == unsubscribeDistributions(bytes32[]).selector) {
		unsubscribeDistributions(e, distributionIds);
    } else if (f.selector == stake(address, uint256, address, address).selector) {
        stake(e, stakingToken, amount, sender, recipient); 
    } else if (f.selector == stakeUsingVault(address, uint256, address, address).selector) {
        stakeUsingVault(e, stakingToken, amount, sender, recipient);
	} else if (f.selector == stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32).selector) {
        stakeWithPermit(e, stakingToken, amount, recipient, deadline, v, r, s);
	} else if (f.selector == unstake(address, uint256, address, address).selector) {
		unstake(e, stakingToken, amount, sender, recipient);
    } else if (f.selector == claim(bytes32[], bool, address, address).selector) {
        claim(e, distributionIds, toInternalBalance, sender, recipient);
    } else if (f.selector == claimWithCallback(bytes32[], address, address, bytes).selector) {
        claimWithCallback(e, distributionIds, sender, callbackContract,callbackData);
	} else if (f.selector == exit(address[], bytes32[]).selector) {
        exit(e, stakingTokens, distributionIds);
	} else if (f.selector == exitWithCallback(address[], bytes32[], address, bytes).selector) {
		exitWithCallback(e, stakingTokens, distributionIds, callbackContract, callbackData);
	} else {
        calldataarg args;
        f(e, args);
    }
}

// Assuming the hash is and correlates the trio properly - full paramater set required
function requireDistIdCorrelatedWithTrio(bytes32 distId, address _stakingToken, address _distributionToken, address _owner){
    // given 3 arbitrary args, the hashing function should retrieve the value distId.
    // also the staking token, distribution token and owner associated with this distId must match the arbitrary values.
    require (uniqueHashGhost(_stakingToken, _distributionToken, _owner) == distId && ((getStakingToken(distId) == _stakingToken && getDistributionToken(distId) == _distributionToken && getOwner(distId) == _owner)));
}

// Assuming the hash is deterministic, and correlates the trio properly
function hashUniquness(bytes32 distId1, address stakingToken1, address distributionToken1, address owner1, bytes32 distId2, address stakingToken2, address distributionToken2, address owner2){
    require (((stakingToken1 != stakingToken2) || (distributionToken1 != distributionToken2) || (owner1 != owner2)) <=> 
    (uniqueHashGhost(stakingToken1, distributionToken1, owner1) != uniqueHashGhost(stakingToken2, distributionToken2, owner2)));
}

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Invariants    /////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// P@P - _indexes mapping and _values array are correlated in the enumerable set
invariant enumerableSetIsCorrelated(address stakingToken, address user, uint256 index, bytes32 distId)
        // ID in mapping declare "not contained", then the array at the index is not distId
        (getUserSubscribedDistributionIndexById(stakingToken, user, distId) == max_uint256 => 
            (getUserSubscribedDistributionIdByIndex(stakingToken, user, index) != distId) && 
        // Id in mapping declare "containd", then the array at index is distId <=> ID in mapping retrieve index 
        getUserSubscribedDistributionIndexById(stakingToken, user, distId) != max_uint256 =>
            ((getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distId && distId != 0) <=> 
                (getUserSubscribedDistributionIndexById(stakingToken, user, distId) == index)))
        {
            preserved unsubscribeDistributions(bytes32[] distributionIdArray) with (env e)
            {
                require distributionIdArray[0] == distId;
            }
        }

// V@V - checks the correlation of the set and _userStaking mapping. If the distId is in the set, the stakingToken associated with this distId is the same as the stakingToken in the mapping.
// If the stakingToken associated to the distId is not the same as the stakingToken leading to the set in the mapping, then the distId shouldn't be in the set.
invariant _userStakingMappingAndSetAreCorrelated(bytes32 distId, address stakingToken, address user)
        (stakingToken == 0 => !getDistIdContainedInUserSubscribedDistribution(stakingToken, user, distId)) &&
        (stakingToken != 0 => (getDistIdContainedInUserSubscribedDistribution(stakingToken, user, distId) => 
                getStakingToken(distId) == stakingToken))
        {
            preserved createDistribution(address stk2, address dst2, uint256 dur2) with (env e)
            {
                requireInvariant distExistInitializedParams(distId, e);
            }
            preserved unsubscribeDistributions(bytes32[] distributionIdArray) with (env e)
            {
                require distributionIdArray[0] == distId;
            }
        }


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


// V@V - A user cannot be subscribed to a distribution that does not exist, and the other way around - if a user is subscribed to a distribution then it has to exist.
invariant notSubscribedToNonExistingDistSet(bytes32 distId, address user)
        (getStakingToken(distId) == 0 => !isSubscribed(distId, user)) &&
            (isSubscribed(distId, user) => getStakingToken(distId) != 0)
        {
            preserved unsubscribeDistributions(bytes32[] distributionIdArray) with (env e)
            {
                address stakingToken; uint256 index;
                requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distId);
            }
        }
 

// F@F - If duration/owner/staking_token/distribution_token are not set, the distribution does not exist
invariant conditionsDistNotExist(bytes32 distId)
        getStakingToken(distId) == 0 <=> distNotExist(distId)
        {
            preserved with (env e)
            {
                address stakingToken; address user; uint256 index; address distributionToken;
                requireDistIdCorrelatedWithTrio(distId, stakingToken, distributionToken, user);
                requireInvariant distExistInitializedParams(distId, e);
                requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distId, stakingToken, user);
                requireInvariant notSubscribedToNonExistingDistSet(distId, user);
            }
        }


// V@V - stakingToken != 0 <=> !distNotExist (distExist) => the state is in **one** of the other 3 definitions.
// @note that this invariant might be covered by oneStateAtATime
invariant conditionsDistExist(bytes32 distId, env e)
        getStakingToken(distId) != 0 => ((distNew(distId) && !distActive(distId, e) && !distFinished(distId, e)) ||
                                        (!distNew(distId) && distActive(distId, e) && !distFinished(distId, e)) ||
                                        (!distNew(distId) && !distActive(distId, e) && distFinished(distId, e)))
        {
            preserved with (env e2)
            {
                require e.msg.sender == e2.msg.sender;
                requireEnvValuesNotZero(e2);
                requireInvariant distExistInitializedParams(distId, e2);
                requireInvariant conditionsDistNotExist(distId);
            }
        }


// V@V - lastUpdateTime, periodFinished are either initialized (!=0) or uninitialized (0) simultaneously
// @note that the commented line - correlation of paymentRate to the mentioned fields - is planed left as a comment, 
// as the dev team plan to limit values of some properties, and add requires that will ensure paymentRate > 0 in the near future.
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


// F@F - The system is in either of the 4 defined states. It cannot be in any other state, nor in more than 1 state at the same time.
invariant oneStateAtATime(bytes32 distId, env e)
        ((distNotExist(distId) && !distNew(distId) && !distActive(distId, e) && !distFinished(distId, e)) ||
        (!distNotExist(distId) && distNew(distId) && !distActive(distId, e) && !distFinished(distId, e)) ||
        (!distNotExist(distId) && !distNew(distId) && distActive(distId, e) && !distFinished(distId, e)) ||
        (!distNotExist(distId) && !distNew(distId) && !distActive(distId, e) && distFinished(distId, e)))
        {
            preserved with (env e2)
            {
                require e.block.timestamp == e2.block.timestamp;
                requireEnvValuesNotZero(e2);
                address stakingToken; address user; uint256 index; address distributionToken;
                requireDistIdCorrelatedWithTrio(distId, stakingToken, distributionToken, user);
                requireInvariant distExistInitializedParams(distId, e2);
                requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distId, stakingToken, user);
                requireInvariant notSubscribedToNonExistingDistSet(distId, user);
            }
        }


// V@V - lastUpdateTime can't be in the future
invariant lastUpdateTimeNotInFuture(env e, bytes32 distributionId)
    getLastUpdateTime(distributionId) <= e.block.timestamp
    {
        preserved with (env e2)
        {
            require e.block.timestamp == e2.block.timestamp;
        }
    }


// V@V - lastUpdateTime cannot be greater than periodFinish
invariant getLastUpdateTimeLessThanFinish(bytes32 distributionId)
    getLastUpdateTime(distributionId) <= getPeriodFinish(distributionId)


// V@V - _lastTimePaymentApplicable is always greater or equal than lastUpdateTime to avoid underflow
invariant validityOfLastTimePaymentApplicable(bytes32 distributionId, env e)
    getLastUpdateTime(distributionId) <= _lastTimePaymentApplicableHarness(e, distributionId)
    {
        preserved with (env e2)
        { 
            require e.block.timestamp == e2.block.timestamp;
        }
    }


// V@V - The global token per stake (gtps) is always greater or equal to the user token per stake (utps) 
invariant gtpsGreaterOrEqualUtps(bytes32 distributionId, address stakingToken, address sender)
        getGlobalTokensPerStake(distributionId) >= getUserTokensPerStake(distributionId, stakingToken, sender)


// CHECK
// The balance of subscribed and staked user should be less than or equal to the totalSupply of a distribution
invariant userSubStakeCorrelationWithTotalSupply(bytes32 distributionId, address user, address token, uint256 index, env e)
    (getDistIdContainedInUserSubscribedDistribution(token, user, distributionId) && getUserBalance(token, user) > 0)
            => (getUserBalance(token, user) <= getTotalSupply(distributionId)) filtered { f -> f.selector != certorafallback_0().selector }
    { 
        preserved with (env e2) 
        {
            require e2.msg.sender == user;
            require getStakingToken(distributionId) == token;
            requireInvariant notSubscribedToNonExistingDistSet(distributionId, user);
            requireInvariant enumerableSetIsCorrelated(token, user, index, distributionId);
        }
        preserved unsubscribeDistributions(bytes32[] distributionIds) with (env e3)
        {
            require distributionIds.length <= 3;
            require distributionIds[0] == distributionId;
            require user == e3.msg.sender;
            require getStakingToken(distributionId) == token;
        }
        preserved stake(address stakingToken, uint256 amount, address sender, address recipient) with (env e4)
        {   
            require user == sender;
            require getStakingToken(distributionId) == token;
            require stakingToken == token;
            require index == 0;
            require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                            getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;
        }
        preserved stakeUsingVault(address stakingToken, uint256 amount, address sender, address recipient) with (env e5)
        {
            require user == sender;
            require getStakingToken(distributionId) == token;
            require stakingToken == token;
            require index == 0;
            require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                            getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;
        }
        preserved stakeWithPermit(address stakingToken, uint256 amount, address sender, uint256 deadline, uint8 v, bytes32 r, bytes32 s) with (env e6)
        {
            require user == sender;
            require getStakingToken(distributionId) == token;
            require stakingToken == token;
            require index == 0;
            require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  &&
                            getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;
        }
        preserved unstake(address stakingToken, uint256 amount, address sender, address recipient) with (env e7)
        {
            require user == sender;
            require getStakingToken(distributionId) == token;
            require stakingToken == token;
            requireInvariant notSubscribedToNonExistingDistSet(distributionId, user);
            requireInvariant enumerableSetIsCorrelated(token, user, index, distributionId);
        }
        preserved exit(address[] stakingTokens, bytes32[] distributionIds) with (env e8)
        {
            require e8.msg.sender == user;
            require getStakingToken(distributionId) == token;
            require stakingTokens.length <= 3;
            require stakingTokens[0] == token;
            require distributionIds[0] == distributionId;
            requireInvariant notSubscribedToNonExistingDistSet(distributionId, user);
            requireInvariant enumerableSetIsCorrelated(token, user, index, distributionId);
        }
        preserved exitWithCallback(address[] stakingTokens, bytes32[] distributionIds, address callbackContract, bytes callbackData) with (env e9)
        {
            require e9.msg.sender == user;
            require getStakingToken(distributionId) == token;
            require stakingTokens.length <= 3;
            require distributionIds.length <= 3;
            require stakingTokens[0] == token;
            require distributionIds[0] == distributionId;
            requireInvariant notSubscribedToNonExistingDistSet(distributionId, user);
            requireInvariant enumerableSetIsCorrelated(token, user, index, distributionId);
        }
    }


/////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////    Rules    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// F@F - fails on stake & unstake - Creating a dist bringing us from the state distNotExist to distNew (no other function does that). All other functions will leave us in distNotExist state.
// @note that we dont check createDistribution for a distribution_ID != distId, counting on another rule, distributionsAreIndependent, that proved any operation on other dists will not effect the one at hand.
rule transition_NotExist_To_DistNew(bytes32 distId) {
    method f; env e; calldataarg args; bytes32[] distIds;

    require distNotExist(distId);
    requireEnvValuesNotZero(e);
    
    address stakingToken; address user; uint256 index; address distributionToken;
    requireDistIdCorrelatedWithTrio(distId, stakingToken, distributionToken, user);
    requireInvariant distExistInitializedParams(distId, e);
    // require index == 0;
    requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distId);
    requireInvariant _userStakingMappingAndSetAreCorrelated(distId, stakingToken, user);
    requireInvariant notSubscribedToNonExistingDistSet(distId, user);

    // calling all functions, making sure the created distr-ibution id is the distId of interest
    callAllFunctionsWithParameters(f, e, distId, distIds, stakingToken, user);
    assert f.selector != createDistribution(address, address, uint256).selector => distNotExist(distId), "distribution changed state without creating a distribution";
    assert f.selector == createDistribution(address, address, uint256).selector => distNew(distId), "distribution did not change due to call to createDistribution function";
}


// V@V - Funding a dist bringing us from the state distNew to distActive (no other function does that). All other functions will leave us in distNew state.
rule transition_DistNew_To_DistActive(bytes32 distId){
    method f; env e; calldataarg args;
    require distNew(distId);
    requireEnvValuesNotZero(e);
    
    callFundDistributionWithSpecificDistId(f, e, distId);
    assert f.selector != fundDistribution(bytes32, uint256).selector <=> distNew(distId), "distribution changed state without funding a distribution";
    assert f.selector == fundDistribution(bytes32, uint256).selector <=> distActive(distId, e), "distribution did not change due to call to fundDistribution function";
}


// V@V - All function calls will leave us in distActive state. only time can change a dist state to finished.
// @note that the require on e2 is being done to simulate elapsing time with gurantee to get timestamp that exceed the periodFinished timestamp.
// We make sure to have the same attribute to the environment.
rule transition_DistActive_To_DistFinished(bytes32 distId){
    method f;  env e; calldataarg args;
    require distActive(distId, e);
    requireEnvValuesNotZero(e);
    f(e, args);
    
    assert distActive(distId, e), "distribution changed state";
    
    env e2;
    requireEnvValuesNotZero(e2);
    require e.msg.sender == e2.msg.sender;
    require e2.block.timestamp > getPeriodFinish(distId);

    assert distFinished(distId, e2), "distribution did not change state to finished even though the finish date has arrived";
}


// V@V - Funding a dist bringing us from the state distFinished back to distActive (no other function does that). All other functions will leave us in distFinished state.
rule transition_DistFinished_To_DistActive(bytes32 distId){
    method f; env e; calldataarg args;
    require distFinished(distId, e);
    requireEnvValuesNotZero(e);
    
    callFundDistributionWithSpecificDistId(f, e, distId);
    assert f.selector != fundDistribution(bytes32, uint256).selector <=> distFinished(distId, e), "distribution changed state without funding a distribution";
    assert f.selector == fundDistribution(bytes32, uint256).selector <=> distActive(distId, e), "distribution did not change due to call to fundDistribution function";
}


// V@V - starting from an initial state where dist 1 & 2 does not exist (all fields are in default values),
// creation of 2 dists (with different ids) must result from 2 different trios. 
// @note that hashUniquness is assuming that for different distIds the trios are not equal,
// therefore the rule is basically weaker than intended, it mainly shows that createDistribution from DistNotExist
// populate the mapping with the distinct trios
rule noTwoTripletsAreTheSameFirstStep(env e, env e2, bytes32 distId1, bytes32 distId2){
    method f; calldataarg args;
    address stk1; address dst1; uint256 dur1;
    address stk2; address dst2; uint256 dur2;

    require (distNotExist(distId1) && distNotExist(distId2));
    bytes32 distId1_return = createDistribution(e, stk1, dst1, dur1);
    bytes32 distId2_return = createDistribution(e2, stk2, dst2, dur2);
 
    hashUniquness(distId1_return, stk1, dst1, e.msg.sender, distId2_return, stk2, dst2, e2.msg.sender);
    requireDistIdCorrelatedWithTrio(distId1_return, stk1, dst1, e.msg.sender);
    requireDistIdCorrelatedWithTrio(distId2_return, stk2, dst2, e2.msg.sender); 

    assert ((distId1 == distId1_return && distId2 == distId2_return) => 
            (getStakingToken(distId1_return) != getStakingToken(distId2_return)) || 
            (getDistributionToken(distId1_return) != getDistributionToken(distId2_return)) || 
            (getOwner(distId1_return) != getOwner(distId2_return)));
}


// V@V - Once 2 distributions has 2 distinct trios constituting them, their trio fields cannot be changed in such a way that will make them equivalent.
rule noTwoTripletsAreTheSame(env e, bytes32 distId1, bytes32 distId2){
    method f; calldataarg args;
    address _stakingToken1; address _distributionToken1; address _owner1;
    address _stakingToken2; address _distributionToken2; address _owner2;

    require (!distNotExist(distId1) && !distNotExist(distId2));
    requireInvariant oneStateAtATime(distId1, e); requireInvariant oneStateAtATime(distId2, e);
    requireDistIdCorrelatedWithTrio(distId1, _stakingToken1, _distributionToken1, _owner1); requireInvariant distExistInitializedParams(distId1, e);
    requireDistIdCorrelatedWithTrio(distId2, _stakingToken2, _distributionToken2, _owner2); requireInvariant distExistInitializedParams(distId2, e);
    require ((getStakingToken(distId1) != getStakingToken(distId2)) || (getDistributionToken(distId1) != getDistributionToken(distId2)) || (getOwner(distId1) != getOwner(distId2)));
    f(e,args);
    assert ((getStakingToken(distId1) != getStakingToken(distId2)) || (getDistributionToken(distId1) != getDistributionToken(distId2)) || (getOwner(distId1) != getOwner(distId2))), "all 3 fields are the same";
}


// V@V - When calling a function on a specific distribution (e.g. subscribe, set duration, fund, etc.), no other distributions are being affected
rule distributionsAreIndependent(method f, bytes32 distId1, bytes32 distId2) {
    env e1; env e2; bytes32[] distIdArray; address stkToken; address recipient;
    address _sToken = getStakingToken(distId1);
    address _dToken = getDistributionToken(distId1);
    address _owner = getOwner(distId1);
    uint256 _totSupply = getTotalSupply(distId1);
    uint256 _duration = getDuration(distId1);
    uint256 _pFinished = getPeriodFinish(distId1);
    uint256 _pRate = getPaymentRate(distId1);
    uint256 _lastUpdateTime = getLastUpdateTime(distId1);
    uint256 _globalTokensPerStake = getGlobalTokensPerStake(distId1);

    require distId2 != distId1;
    require distIdArray.length <= 1 && distIdArray[0] != distId1;
    callAllFunctionsWithParameters(f, e2, distId2, distIdArray, stkToken, recipient);

    address sToken_ = getStakingToken(distId1);
    address dToken_ = getDistributionToken(distId1);
    address owner_ = getOwner(distId1);
    uint256 totSupply_ = getTotalSupply(distId1);
    uint256 duration_ = getDuration(distId1);
    uint256 pFinished_ = getPeriodFinish(distId1);
    uint256 pRate_ = getPaymentRate(distId1);
    uint256 lastUpdateTime_ = getLastUpdateTime(distId1);
    uint256 globalTokensPerStake_ = getGlobalTokensPerStake(distId1);

    assert sToken_ == _sToken, "staking token changed";
    assert dToken_ == _dToken, "dist token changed";
    assert owner_ == _owner, "owner changed";
    assert ((totSupply_ == _totSupply) || (nonSpecificDistribution(f) <=> (totSupply_ != _totSupply))), "totSupply changed not due to stake/unstake/exit";
    assert duration_ == _duration, "duration changed";
    assert pFinished_ == _pFinished, "period finished changed";
    assert pRate_ == _pRate, "payment rate changed";
    assert ((lastUpdateTime_ == _lastUpdateTime) || (nonSpecificDistribution(f) <=> (lastUpdateTime_ != _lastUpdateTime))) , "last update time changed not due to stake/unstake/exit";
    assert ((globalTokensPerStake_ == _globalTokensPerStake) || (nonSpecificDistribution(f) <=> (globalTokensPerStake_ != _globalTokensPerStake))), "global Tokens Per Stake changed not due to stake/unstake/exit";
}


// CLEANED
// globalTokensPerStake is non-decreasing 
rule gtpsMonotonicity(bytes32 distributionId, method f){
        uint256 gtpsBefore = getGlobalTokensPerStake(distributionId);

        env e;
        calldataarg args;
        f(e, args);

        uint256 gtpsAfter = getGlobalTokensPerStake(distributionId);

        assert gtpsBefore <= gtpsAfter, "gtps was decreased";
}


// CLEANED
// userTokensPerStake is non-decreasing 
rule utpsMonotonicity(bytes32 distributionId, method f, address stakingToken, address user, uint256 index) filtered { f -> f.selector != certorafallback_0().selector} {
        requireInvariant gtpsGreaterOrEqualUtps(distributionId, stakingToken, user);

        uint256 utpsBefore = getUserTokensPerStake(distributionId, stakingToken, user);

        env e;
        calldataarg args;
        f(e, args);

        uint256 utpsAfter = getUserTokensPerStake(distributionId, stakingToken, user);

        assert utpsBefore <= utpsAfter, "utps was decreased";
}


// CLEANED
// lastUpdateTime is non-decreasing 
rule lastUpdateTimeMonotonicity(bytes32 distributionId, address stakingToken, address sender, method f, env e){
        requireInvariant lastUpdateTimeNotInFuture(e, distributionId);
        require !distNotExist(distributionId);
        requireInvariant getLastUpdateTimeLessThanFinish(distributionId);

        uint256 lastUpdateTimeBefore = getLastUpdateTime(distributionId);

        calldataarg args;
        f(e, args);

        uint256 lastUpdateTimeAfter = getLastUpdateTime(distributionId);

        assert lastUpdateTimeBefore <= lastUpdateTimeAfter, "lastUpdateTime was decreased";
}


// CLEANED
// Check that each possible operation changes the balance of at most one user
rule balanceOfChange(address userA, address userB, address stakingToken,  method f) {
	require userA != userB;

	uint256 balanceABefore = getUserBalance(stakingToken, userA);
	uint256 balanceBBefore = getUserBalance(stakingToken, userB);
	 
    env e; 
	calldataarg args;
	f(e, args); 
	
    uint256 balanceAAfter = getUserBalance(stakingToken, userA);
    uint256 balanceBAfter = getUserBalance(stakingToken, userB);

	assert (balanceABefore == balanceAAfter || balanceBBefore == balanceBAfter),"balances of two users were affected";
}


// CHECK
// Check that the changes to total supply are coherent with the changes to balance
rule integrityBalanceOfTotalSupply(address user, address distributionToken, address stakingToken, bytes32 distributionId, uint256 index, method f, env e) filtered { f -> f.selector != certorafallback_0().selector} {
    require e.msg.sender == user;
    require getStakingToken(distributionId) == stakingToken;
    require getDistributionToken(distributionId) == distributionToken;
    requireInvariant userSubStakeCorrelationWithTotalSupply(distributionId, user, stakingToken, index, e);
    
	uint256 balanceABefore = getUserBalance(stakingToken, user);
	uint256 totalSupplyBefore = getTotalSupply(distributionId);

	integrityHelper(f, e, distributionId, user, distributionToken, stakingToken); 

	uint256 balanceAAfter = getUserBalance(stakingToken, user);
	uint256 totalSupplyAfter = getTotalSupply(distributionId);

	assert (balanceAAfter != balanceABefore) 
                => (balanceAAfter - balanceABefore  == totalSupplyAfter - totalSupplyBefore), "not correlated";
}


function integrityHelper(method f, env e, bytes32 distributionId, address user, address distributionToken, address stakingToken){
    uint256 amount; uint256 deadline; uint8 v; 
    bytes32[] distributionIds; 
    bytes32 r; bytes32 s; 
    bytes callbackData; 
    address[] stakingTokens;
    address callbackContract; 
    
    require distributionIds.length == 1;
    require distributionIds[0] == distributionId;

    require stakingTokens.length == 1;
    require stakingTokens[0] == stakingToken;

    uint256 index;
    require index == 0;
    require getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distributionId  
                && getUserSubscribedDistributionIndexById(stakingToken, user, distributionId) == index;

	if (f.selector == stake(address, uint256, address, address).selector) {
        stake(e, stakingToken, amount, user, user); 
    } else if (f.selector == stakeUsingVault(address, uint256, address, address).selector) {
        stakeUsingVault(e, stakingToken, amount, user, user);
	} else if  (f.selector == stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32).selector) {
        stakeWithPermit(e, stakingToken, amount, user, deadline, v, r, s);
	} else if (f.selector == unstake(address, uint256, address, address).selector) {
		unstake(e, stakingToken, amount, user, user);
    }  else if  (f.selector == exit(address[], bytes32[]).selector) {
        exit(e, stakingTokens, distributionIds);
	} else if (f.selector == exitWithCallback(address[], bytes32[], address, bytes).selector) {
		exitWithCallback(e, stakingTokens, distributionIds, callbackContract, callbackData);
	} else {
        calldataarg args;
        f(e, args);
    }
}


// CLEANED
// The duration cannot be changed if distribution is active
rule unchangedDurationDuringActiveDistribution(bytes32 distributionId, method f, env e){
    require distActive(distributionId, e);

    uint256 durationBefore = getDuration(distributionId);

    calldataarg args;
    f(e, args);

    uint256 durationAfter = getDuration(distributionId);

    assert durationBefore == durationAfter;
}

// CLEANED
// The owner of a distribution cannot be changed
rule permanentOwner(bytes32 distributionId, method f, env e){
    require distNew(distributionId) || distActive(distributionId, e) || distFinished(distributionId, e);

    address ownerBefore = getOwner(distributionId);

    calldataarg args;
    f(e, args);

    address ownerAfter = getOwner(distributionId);

    assert ownerAfter == ownerBefore;
}

// CLEANED
// total assets of a user (in Vault and in ERC Token) plus unclaimed tokens should be equal to the total assets of a user after claim function is called
rule claimCorrectnessCheckForOneUser(address dstToken, address sender, address recipient, bytes32 distributionId, uint256 index){
    env e;
    bool toInternalBalance;
    bytes32[] distributionIds;
    
    require getDistributionToken(distributionId) == dstToken;
    require Vault != recipient;
    require recipient != currentContract;    
    require distributionIds.length == 1;
    require distributionIds[0] == distributionId;

    uint256 vaultAndTokenBalanceBefore = Vault.totalAssetsOfUser(e, dstToken, recipient);

    uint256 shouldBeClaimed = getClaimableTokens(e, distributionId, sender);

    claim(e, distributionIds, toInternalBalance, sender, recipient);

    uint256 vaultAndTokenBalanceAfter = Vault.totalAssetsOfUser(e, dstToken, recipient);

    mathint all = vaultAndTokenBalanceBefore + shouldBeClaimed;

    assert all == to_mathint(vaultAndTokenBalanceAfter), "total asssets are not the same";
}


// CLEANED
// There is no way to claim reward twice at the same block timestamp (check for no reclaim)
rule noReclaim(address dstToken, address sender, address recipient, bytes32 distributionId, uint256 index){
    env e;
    bool toInternalBalance;
    bytes32[] distributionIds;
    
    require getDistributionToken(distributionId) == dstToken;
    require Vault != recipient;
    require recipient != currentContract;    
    require distributionIds.length == 1;
    require distributionIds[0] == distributionId;

    claim(e, distributionIds, toInternalBalance, sender, recipient);

    uint256 shouldBeClaimedAfter = getClaimableTokens(e, distributionId, sender);

    assert shouldBeClaimedAfter == 0, "shouldBeClaimedAfter isn't 0";
}


// CLEANED
// user A can't claim user B's reward (no frontrunning)
rule itIsOnlyMyReward(address dstToken, bytes32 distributionId, address sender){
    env e;
    address userA; address userB;
    bool toInternalBalance;
    bytes32[] distributionIds;

    require isSubscribed(distributionId, sender); require isSubscribed(distributionId, userB);
    require getDistributionToken(distributionId) == dstToken;
    require distributionIds.length == 1;
    require distributionIds[0] == distributionId;
    require sender != userB;
    require userA != userB;

    uint256 userBShouldClaimBefore = getClaimableTokens(e, distributionId, userB);

    claim(e, distributionIds, toInternalBalance, sender, userA);

    uint256 userBShouldClaimAfter = getClaimableTokens(e, distributionId, userB);

    assert userBShouldClaimBefore == userBShouldClaimAfter;
}


// solvency for 1 user
rule solvencyForOneUser(address dstToken, address stkToken, bytes32 distributionId, method f) filtered { f -> !f.isView 
                                                    && f.selector != certorafallback_0().selector } {
    env e; 
    
    address user;
    uint256 amount; uint256 index;

    require Vault != user;
    require user != currentContract;
    require index == 0;
    require dstToken == stkToken;
    
    require getDistributionToken(distributionId) == dstToken;
    require getStakingToken(distributionId) == stkToken;
    // require getUserSubscribedDistributionIdByIndex(stkToken, user, index) == distributionId;
    requireInvariant enumerableSetIsCorrelated(stkToken, user, index, distributionId);

    uint256 claimableTokensBefore = getClaimableTokens(e, distributionId, user);
    uint256 userBalanceBefore = getUserBalance(stkToken, user);
    uint256 vaultAndTokenBalanceBefore = Vault.totalAssetsOfUser(e, dstToken, user);

    mathint combinedBalanceBefore = claimableTokensBefore + userBalanceBefore + vaultAndTokenBalanceBefore;

    solvencyHelper(f, e, distributionId, user, dstToken, stkToken);

    uint256 claimableTokensAfter = getClaimableTokens(e, distributionId, user);
    uint256 userBalanceAfter = getUserBalance(stkToken, user);
    uint256 vaultAndTokenBalanceAfter = Vault.totalAssetsOfUser(e, dstToken, user);

    mathint combinedBalanceAfter = claimableTokensAfter + userBalanceAfter + vaultAndTokenBalanceAfter;

    assert combinedBalanceBefore == combinedBalanceAfter, "balances are not equal";
}


function solvencyHelper(method f, env e, bytes32 distributionId, address user, address distributionToken, address stakingToken){
    uint256 duration; uint256 amount; uint256 deadline;
    uint8 v; bytes32 r; bytes32 s;
    bytes32[] distributionIds; address[] stakingTokens;
    bool toInternalBalance; address callbackContract; bytes callbackData; 

    require distributionIds.length == 1;
    require distributionIds[0] == distributionId;

    require stakingTokens.length == 1;
    require stakingTokens[0] == stakingToken;

	if (f.selector == createDistribution(address, address, uint256).selector) {
        bytes32 distId = createDistribution(e, stakingToken, distributionToken, duration);
        require distId == distributionId;
	} else if (f.selector == setDistributionDuration(bytes32, uint256).selector) {
        setDistributionDuration(e, distributionId, duration);
	} else if (f.selector == fundDistribution(bytes32, uint256).selector) {
        require e.msg.sender != user;
		fundDistribution(e, distributionId, amount);
	} else if (f.selector == subscribeDistributions(bytes32[]).selector) {
        subscribeDistributions(e, distributionIds);
	} else if (f.selector == unsubscribeDistributions(bytes32[]).selector) {
		unsubscribeDistributions(e, distributionIds);
    } else if (f.selector == stake(address, uint256, address, address).selector) {
        require isSubscribed(distributionId, user);
        stake(e, stakingToken, amount, user, user); 
    } else if (f.selector == stakeUsingVault(address, uint256, address, address).selector) {
        require isSubscribed(distributionId, user);
        stakeUsingVault(e, stakingToken, amount, user, user);
	} else if  (f.selector == stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32).selector) {
        require isSubscribed(distributionId, user);
        stakeWithPermit(e, stakingToken, amount, user, deadline, v, r, s);
	} else if (f.selector == unstake(address, uint256, address, address).selector) {
        require isSubscribed(distributionId, user);
		unstake(e, stakingToken, amount, user, user);
    } else if (f.selector == claim(bytes32[], bool, address, address).selector) {
        claim(e, distributionIds, toInternalBalance, user, user);
    } else if (f.selector == claimWithCallback(bytes32[], address, address, bytes).selector) {
        require callbackContract == user;
        claimWithCallback(e, distributionIds, user, callbackContract, callbackData);
	} else if  (f.selector == exit(address[], bytes32[]).selector) {
        require isSubscribed(distributionId, user);
        exit(e, stakingTokens, distributionIds);
	} else if (f.selector == exitWithCallback(address[], bytes32[], address, bytes).selector) {
        require isSubscribed(distributionId, user);
        require e.msg.sender == user;
        require callbackContract == user;
		exitWithCallback(e, stakingTokens, distributionIds, callbackContract, callbackData);
	} else {
        calldataarg args;
        f(e, args);
    }
}


// The order of actions in the same block should have no effect on the state of the user 
// Sub/Stake    Unsub/Unstake       Claim/Stake                           Exit/Unstake_Claim
rule orderMakesNoDifferenceOnOneBlock(bytes32 distributionId, method f){
    bytes32[] distributionIds;
    address stakingToken; address distributionToken; address sender; address recipient;
    uint256 amount;
    env e;

    require sender == recipient;
    require e.msg.sender == recipient;
    require distributionIds[0] == distributionId;
    require getStakingToken(distributionId) == stakingToken;
    require getDistributionToken(distributionId) == distributionToken;

    storage initialStorage = lastStorage;

    stake(e, stakingToken, amount, sender, recipient);
    subscribeDistributions(e, distributionIds);

    uint256 userBalanceFirst = getUserBalance(stakingToken, sender);
    uint256 distTotalSupplyFirst = getTotalSupply(distributionId);
    uint256 vaultAndTokenBalanceFirst = Vault.totalAssetsOfUser(e, distributionToken, recipient);
    uint256 getGTPSFirst = getGlobalTokensPerStake(distributionId);
    uint256 getUTPSFirst = getUserTokensPerStake(distributionId, stakingToken, recipient);
    bool isSubscribedFirst = isSubscribed(distributionId, sender);

    subscribeDistributions(e, distributionIds) at initialStorage;
    stake(e, stakingToken, amount, sender, recipient);

    uint256 userBalanceSecond = getUserBalance(stakingToken, sender);
    uint256 distTotalSupplySecond = getTotalSupply(distributionId);
    uint256 vaultAndTokenBalanceSecond = Vault.totalAssetsOfUser(e, distributionToken, recipient);
    uint256 getGTPSSecond = getGlobalTokensPerStake(distributionId);
    uint256 getUTPSSecond = getUserTokensPerStake(distributionId, stakingToken, recipient);
    bool isSubscribedSecond = isSubscribed(distributionId, sender);

    assert  userBalanceFirst == userBalanceSecond
                && distTotalSupplyFirst == distTotalSupplySecond 
                && vaultAndTokenBalanceFirst == vaultAndTokenBalanceSecond 
                && getGTPSFirst == getGTPSSecond
                && getUTPSFirst == getUTPSSecond
                && isSubscribedFirst == isSubscribedSecond, "states are different";
}
