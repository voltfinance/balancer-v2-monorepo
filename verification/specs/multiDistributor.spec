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

    // view functions
    isSubscribed(bytes32, address) returns bool envfree
    // getDistributionId(address stakingToken, address distributionToken, address owner) returns bytes32 envfree => uniqueHash(stakingToken, distributionToken, owner)
    getDistributionId(address, address, address) returns bytes32 envfree

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
    // dummyUserSubscriptions(address, address, bytes32) returns bool envfree
    _lastTimePaymentApplicable(address) returns uint256

    totalAssetsOfUser(address, address) returns uint256 => DISPATCHER(true)
    manageUserBalance((uint8,address,uint256,address,address)[]) => DISPATCHER(true)
    balanceOf(address) returns uint256 => DISPATCHER(true)
    transfer(address, uint256) returns bool => DISPATCHER(true)
    transferFrom(address, address, uint256) returns bool => DISPATCHER(true)
    
    getUserUnclaimedTokensOfDistribution(bytes32, address, address) returns uint256
    getClaimableTokens(bytes32, address) returns uint256
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
        // getPaymentRate(distId) != 0 && 
        (getLastUpdateTime(distId) != 0 && getLastUpdateTime(distId) <= getPeriodFinish(distId)); //&&
        // if everybody stake then unstake at some point GTPS, total supply can be 0, yet GTPS != 0
        // if at least 1 user is staked and subscribe then GTPS != 0
        // (getTotalSupply(distId) == 0 ? getGlobalTokensPerStake(distId) == 0 : getGlobalTokensPerStake(distId) != 0);

// Dist Finished, not active - 4 non-zero parameters from distCreated + 4 more.
// payment rate is assumed to be non-zero once dist if funded. that means that the funder of the dist always make sure that amount > duration.
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

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Helpers    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// making sure the env does not take any 0 values which aren't realistic anyway
function requireEnvValuesNotZero(env e){
    require e.msg.sender != 0;
    require e.block.number != 0;
    require e.block.timestamp != 0;
}

function callCreateDistributionWithSpecificDistId(method f, env e, bytes32 distId, address _stakingToken, address _distributionToken, uint256 _duration){
    if (f.selector == createDistribution(address, address, uint256).selector) {
        bytes32 distributionId = createDistribution(e, _stakingToken, _distributionToken, _duration);
        require distributionId == distId;
    } else {
        calldataarg args;
        f(e, args);
    }
}

function callFundDistributionWithSpecificDistId(method f, env e, bytes32 distId, uint256 _amount){
    if (f.selector == fundDistribution(bytes32, uint256).selector) {
        fundDistribution(e, distId, _amount);
    } else {
        calldataarg args;
        f(e, args);
    }
}


function callAllFunctionsWithParameters(method f, env e, bytes32 distributionId, bytes32[] _distributionIds){
    address stakingToken; address distributionToken; uint256 duration; uint256 amount;
    address sender; address recipient; uint256 deadline; uint8 v; bytes32 r; bytes32 s;
    bool toInternalBalance; address callbackContract; bytes callbackData; address[] stakingTokens;

	if (f.selector == createDistribution(address, address, uint256).selector) {
        bytes32 distId = createDistribution(e, stakingToken, distributionToken, duration);
        require distId == distributionId;
	} else if (f.selector == setDistributionDuration(bytes32, uint256).selector) {
        setDistributionDuration(e, distributionId, duration);
	} else if (f.selector == fundDistribution(bytes32, uint256).selector) {
		fundDistribution(e, distributionId, amount);
	} else if (f.selector == subscribeDistributions(bytes32[]).selector) {
        subscribeDistributions(e, _distributionIds);
	} else if (f.selector == unsubscribeDistributions(bytes32[]).selector) {
		unsubscribeDistributions(e, _distributionIds);
    } else if (f.selector == stake(address, uint256, address, address).selector) {
        stake(e, stakingToken, amount, sender, recipient); 
    } else if (f.selector == stakeUsingVault(address, uint256, address, address).selector) {
        stakeUsingVault(e, stakingToken, amount, sender, recipient);
	} else if  (f.selector == stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32).selector) {
        stakeWithPermit(e, stakingToken, amount, recipient, deadline, v, r, s);
	} else if (f.selector == unstake(address, uint256, address, address).selector) {
		unstake(e, stakingToken, amount, sender, recipient);
    } else if (f.selector == claim(bytes32[], bool, address, address).selector) {
        claim(e, _distributionIds, toInternalBalance, sender, recipient);
    } else if (f.selector == claimWithCallback(bytes32[], address, address, bytes).selector) {
        claimWithCallback(e, _distributionIds, sender, callbackContract,callbackData);
	} else if  (f.selector == exit(address[], bytes32[]).selector) {
        exit(e, stakingTokens, _distributionIds);
	} else if (f.selector == exitWithCallback(address[], bytes32[], address, bytes).selector) {
		exitWithCallback(e, stakingTokens, _distributionIds, callbackContract, callbackData);
	} else {
        calldataarg args;
        f(e, args);
    }
}


// assuming the hash is deterministic, and correlates the trio properly
function requireDistIdCorrelatedWithTrio(bytes32 distId, address _stakingToken, address _distributionToken, address _owner){
    // given 3 arbitrary args, the hashing function should retrieve the value distId.
    // also the staking token, distribution token and owner associated with this distId must match the arbitrary values.
    require (getDistributionId(_stakingToken, _distributionToken, _owner) == distId && ((getStakingToken(distId) == _stakingToken && getDistributionToken(distId) == _distributionToken && getOwner(distId) == _owner)));
}

// a setup function, requiring every invariant in the spec.
function setUp(env e, bytes32 distId, address _stakingToken, address _distributionToken, address _user, uint256 _index){
    requireEnvValuesNotZero(e);
    requireDistIdCorrelatedWithTrio(distId, _, _, _);

    requireInvariant enumerableSetIsCorrelated(_stakingToken, _user, _index, distId);
    requireInvariant _userStakingMappingAndSetAreCorrelated(distId, _stakingToken, _user);
    requireInvariant distExistInitializedParams(distId, e);
    requireInvariant notSubscribedToNonExistingDistSet(distId, _user);
    requireInvariant conditionsDistNotExist(distId);
    requireInvariant conditionsDistExist(distId, e);
    requireInvariant distActivatedAtLeastOnceParams(distId, e);
    // requireInvariant oneStateAtATime(distId, e);
    // requireInvariant lastUpdateTimeNotInFuture(e, distId);
    // requireInvariant getLastUpdateTimeLessThanFinish(distId);
    // requireInvariant globalGreaterOrEqualUser(distId, _stakingToken, _user);
    // requireInvariant userSubStakeCorrelationWithTotalSupply(distId, _user, _stakingToken, _index, e);
    // requireInvariant validityOfLastTimePaymentApplicable(distId, rand, e);
}

// function nonDistributionSpecificFunctions(method f){
//     f.selector == stake(address, uint256, address, address).selector && 
//     f.selector != stakeUsingVault(address, uint256, address, address).selector && 
//     f.selector != stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32).selector && 
//     f.selector != unstake(address, uint256, address, address).selector && 
//     f.selector != exit(address[], bytes32[]).selector && 
//     f.selector != exitWithCallback(address[], bytes32[], address, bytes).selector;
// }

/////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////    Ghost    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// ghost uniqueHash(address, address, address) returns bytes32{
//     axiom forall address stakingToken1. forall address distributionToken1. forall address owner1. 
//                  forall address stakingToken2. forall address distributionToken2. forall address owner2.
//                  ((stakingToken1 != stakingToken2) || (distributionToken1 != distributionToken2) ||
//                  (owner1 != owner2)) => 
//                  (uniqueHash(stakingToken1, distributionToken1, owner1) != uniqueHash(stakingToken2, distributionToken2, owner2));
// }

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Invariants    /////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// V@V - _indexes mapping and _values array are correlated in the enumerable set
invariant enumerableSetIsCorrelated(address stakingToken, address user, uint256 index, bytes32 distId)
        getUserSubscribedDistributionIdByIndex(stakingToken, user, index) == distId <=> getUserSubscribedDistributionIndexById(stakingToken, user, distId) == index
        {
            preserved unsubscribeDistributions(bytes32[] distributionIdArray) with (env e)
            {
                require distributionIdArray[0] == distId;
            }
        }


// V@V - Might be vacious - checks the correlation of the set and _userStaking mapping. If the distId is in the set, the stakingToken associated with this distId is the same as the stakingToken in the mapping.
// If the stakingToken associated to the distId is not the same as the stakingToken leading to the set in the mapping, then the distId shouldn't be in the set.
invariant _userStakingMappingAndSetAreCorrelated(bytes32 distId, address stakingToken, address user)
        (getDistIdContainedInUserSubscribedDistribution(stakingToken, user, distId) => getStakingToken(distId) == stakingToken)
        {
            preserved
            {
                requireDistIdCorrelatedWithTrio(distId, _, _, _);
            }
            preserved unsubscribeDistributions(bytes32[] distributionIdArray) with (env e)
            {
                require distributionIdArray[0] == distId;
            }
        }


/*
// V@V - A distribution ID contained in an enumerable set should be correlated with the ERC20 token that contains the set in _userStaking mapping
invariant userSubscriptionMappingAndSetAreCorrelated(bytes32 distId, address stakingToken, address user)
        // if the distId retrieved by the mapping != 0, then the stakingToken associated with the distId in the struct is the same stakingToken that got us the distId in the mapping 
        ((dummyUserSubscriptions(stakingToken, user, distId) && distId != 0) => 
            getStakingToken(distId) == stakingToken)
        {
            preserved
            {
                uint256 index;
                requireDistIdCorrelatedWithTrio(distId, _, _, _);
            }
        }
 */


// F@F - Could be vacious - distribution ID cannot be changed once set
/*
invariant distIdCannotChangeOnceSet(bytes32 distId)
        getStakingToken(distId) != 0 => distId != 0
*/


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
// This invariant refer to the enumerable set in the original contracts, as oppose to the next invariant that addresses the mapping created in the harness dummyUserSubscriptions.
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

/*
// V@V - A user cannot be subscribed to a distribution that does not exist, and the other way around - if a user is subscribed to a distribution then it has to exist.
// This invariant refer to the mapping created in the harness dummyUserSubscriptions, as oppose to the previous invariant that addresses the enumerable set in the original contracts.
invariant notSubscribedToNonExistingDistMap(bytes32 distId, address stakingToken, address user)
        (getStakingToken(distId) == 0 => (!dummyUserSubscriptions(stakingToken, user, distId) || distId == 0)) &&
            ((dummyUserSubscriptions(stakingToken, user, distId) && distId != 0) => getStakingToken(distId) != 0)
*/

// V@V - If duration/owner/staking_token/distribution_token are not set, the distribution does not exist
invariant conditionsDistNotExist(bytes32 distId)
        getStakingToken(distId) == 0 <=> distNotExist(distId)
        {
            preserved with (env e)
            {
                address stakingToken; address user; uint256 index;
                requireDistIdCorrelatedWithTrio(distId, _, _, _);
                requireInvariant distExistInitializedParams(distId, e);
                requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distId, stakingToken, user);
                requireInvariant notSubscribedToNonExistingDistSet(distId, user);
            }
        }


// V@V - stakingToken != 0 <=> !distNotExist (distExist) => the state is in **one** of the other 3 definitions.
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


// V@V - paymentRate is failing understandably. lastUpdateTime, periodFinished and PaymentRate are either initialized (!=0) or uninitialized (0) simultaneously
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


// V@V - The system is in either of the 4 defined states. It cannot be in any other state, nor in more than 1 state at the same time.
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
                address stakingToken; address user; uint256 index;
                requireDistIdCorrelatedWithTrio(distId, _, _, _);
                requireInvariant distExistInitializedParams(distId, e2);
                requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distId);
                requireInvariant _userStakingMappingAndSetAreCorrelated(distId, stakingToken, user);
                requireInvariant notSubscribedToNonExistingDistSet(distId, user);
            }
        }


// lastUpdateTime can't be in the future
invariant lastUpdateTimeNotInFuture(env e, bytes32 distributionId)
    getLastUpdateTime(distributionId) <= e.block.timestamp
    {
        preserved with (env e2)
        {
            require e.block.timestamp == e2.block.timestamp;
        }
    }


// lastUpdateTime cannot be greater than periodFinish
invariant getLastUpdateTimeLessThanFinish(bytes32 distributionId)
    getLastUpdateTime(distributionId) <= getPeriodFinish(distributionId)


// V@V - The global reward token per stake token var is always greater or equal to the user's reward token per stake token 
invariant globalGreaterOrEqualUser(bytes32 distributionId, address stakingToken, address sender)
        getGlobalTokensPerStake(distributionId) >= getUserTokensPerStake(distributionId, stakingToken, sender)


// Subscribed and staked user's balance should be less or equal than/to the totalSupply of a distribution
invariant userSubStakeCorrelationWithTotalSupply(bytes32 distributionId, address user, address token, uint256 index, env e)
    (isSubscribed(distributionId, user) && getUserBalance(token, user) > 0)
            => (getUserBalance(token, user) <= getTotalSupply(distributionId))
    { 
        preserved with (env e2) 
        {
            require e2.msg.sender == user;
            require getStakingToken(distributionId) == token;
            requireInvariant notSubscribedToNonExistingDist(distributionId, user);
            requireInvariant enumerableSetIsCorrelated(token, user, index, distributionId);
        }
        preserved unstake(address stakingToken, uint256 amount, address sender, address recipient) with (env e3)
        {
            require user == sender;
            require getStakingToken(distributionId) == token;
            require stakingToken == token;
            requireInvariant notSubscribedToNonExistingDist(distributionId, user);
            requireInvariant enumerableSetIsCorrelated(token, user, index, distributionId);
        }
        preserved exit(address[] stakingTokens, bytes32[] distributionIds) with (env e4)
        {
            require e4.msg.sender == user;
            require getStakingToken(distributionId) == token;
            require stakingTokens.length <= 3; // max_uint / 32;
            require stakingTokens[0] == token;
            require distributionIds[0] == distributionId;
            requireInvariant notSubscribedToNonExistingDist(distributionId, user);
            requireInvariant enumerableSetIsCorrelated(token, user, index, distributionId);
        }
        preserved exitWithCallback(address[] stakingTokens, bytes32[] distributionIds, address callbackContract, bytes callbackData) with (env e5)
        {
            require e5.msg.sender == user;
            require getStakingToken(distributionId) == token;
            require stakingTokens.length <= 3; // max_uint / 32;
            require distributionIds.length <= 3; // max_uint / 32;
            require stakingTokens[0] == token;
            require distributionIds[0] == distributionId;
            requireInvariant notSubscribedToNonExistingDist(distributionId, user);
            requireInvariant enumerableSetIsCorrelated(token, user, index, distributionId);
        }
    }


// @AK - not sure in correctness of it
// _lastTimePaymentApplicable should always be greater than distribution.lastUpdateTime to avoid underflow
invariant validityOfLastTimePaymentApplicable(bytes32 distributionId, address rand, env e)
        getLastUpdateTime(distributionId) <= _lastTimePaymentApplicable(e, rand)


/////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////    Rules    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// V@V - Creating a dist bringing us from the state distNotExist to distNew (no other function does that). All other functions will leave us in distNotExist state.
// @note that we dont check createDistribution for a distribution_ID != distId, assuming that any operation on other dists will not effect this one.
rule transition_NotExist_To_DistNew(bytes32 distId) {
    method f; env e; calldataarg args;
    require distNotExist(distId);
    setUp(e, distId, _, _, _, _);
    
    // calling all functions, making sure the created distr-ibution id is the distId of interest
    callCreateDistributionWithSpecificDistId(f, e, distId, _, _, _);
    assert f.selector != createDistribution(address, address, uint256).selector <=> distNotExist(distId), "distribution changed state without creating a distribution";
    assert f.selector == createDistribution(address, address, uint256).selector <=> distNew(distId), "distribution did not change due to call to createDistribution function";
}


// V@V - All function calls will leave us in distActive state. only time can change a dist state to finished.
// @note that the require on e is being done after the function call to simulate elapsing time with gurantee to get timestamp that exceed the periodFinished timestamp.
rule transition_DistActive_To_DistFinished(bytes32 distId){
    method f;  env e; calldataarg args;
    require distActive(distId, e);
    requireEnvValuesNotZero(e);
    // require e2.msg.sender == e.msg.sender;

    f(e, args);

    // require e2.block.timestamp > getPeriodFinish(distId);
    require e.block.timestamp > getPeriodFinish(distId);

    assert distActive(distId, e), "distribution changed state";
    assert distFinished(distId, e), "distribution did not change state to finished even though the finish date has arrived";
}


// V@V - Funding a dist bringing us from the state distFinished back to distActive (no other function does that). All other functions will leave us in distFinished state.
rule transition_DistFinished_To_DistActive(bytes32 distId){
    method f; env e; calldataarg args;
    require distFinished(distId, e);
    requireEnvValuesNotZero(e);
    
    // calling all functions, making sure the created distribution id is the distId of interest
    callFundDistributionWithSpecificDistId(f, e, distId, _);
    assert f.selector != fundDistribution(bytes32, uint256).selector <=> distFinished(distId, e), "distribution changed state without funding a distribution";
    assert f.selector == fundDistribution(bytes32, uint256).selector <=> distActive(distId, e), "distribution did not change due to call to fundDistribution function";
}


// V@V - Funding a dist bringing us from the state distNew to distActive (no other function does that). All other functions will leave us in distNew state.
rule transition_DistNew_To_DistActive(bytes32 distId){
    method f; env e; calldataarg args;
    require distNew(distId);
    requireEnvValuesNotZero(e);
    
    // calling all functions, making sure the created distribution id is the distId of interest
    callFundDistributionWithSpecificDistId(f, e, distId, _);
    assert f.selector != fundDistribution(bytes32, uint256).selector <=> distNew(distId), "distribution changed state without funding a distribution";
    assert f.selector == fundDistribution(bytes32, uint256).selector <=> distActive(distId, e), "distribution did not change due to call to fundDistribution function";
}


// F@F - failing creating valid distIds with no pre assumptions
rule noTwoTripletsAreTheSameFirstStep(env e, env e2, bytes32 distId1, bytes32 distId2){
    method f; calldataarg args;
    address stk1; address dst1; uint256 dur1;
    address stk2; address dst2; uint256 dur2;

    require (distNotExist(distId1) && distNotExist(distId2));
    bytes32 distId1_return = createDistribution(e, stk1, dst1, dur1);
    bytes32 distId2_return = createDistribution(e2, stk2, dst2, dur2);
    requireDistIdCorrelatedWithTrio(distId1_return, stk1, dst1, e.msg.sender); //requireInvariant distExistInitializedParams(distId1_return, e);
    requireDistIdCorrelatedWithTrio(distId2_return, stk2, dst2, e2.msg.sender); //requireInvariant distExistInitializedParams(distId2_return, e2);
    assert ((distId1 == distId1_return && distId2 == distId2_return) => 
            (getStakingToken(distId1_return) != getStakingToken(distId2_return)) || 
            (getDistributionToken(distId1_return) != getDistributionToken(distId2_return)) || 
            (getOwner(distId1_return) != getOwner(distId2_return)));
}


// V@V - Once 2 distributions has 2 different trios constituting them, their trio fields cannot be changed in such a way that will make them equivalent.
rule noTwoTripletsAreTheSame(env e, bytes32 distId1, bytes32 distId2){
    method f; calldataarg args;
    requireDistIdCorrelatedWithTrio(distId1, _, _, _); requireInvariant distExistInitializedParams(distId1, e);
    requireDistIdCorrelatedWithTrio(distId2, _, _, _); requireInvariant distExistInitializedParams(distId2, e);
    require ((getStakingToken(distId1) != getStakingToken(distId2)) || (getDistributionToken(distId1) != getDistributionToken(distId2)) || (getOwner(distId1) != getOwner(distId2)));
    f(e,args);
    bool exp = ((getStakingToken(distId1) != getStakingToken(distId2)) || (getDistributionToken(distId1) != getDistributionToken(distId2)) || (getOwner(distId1) != getOwner(distId2)));
    assert (exp, "after calling f");
}

// // vacious using lastStorage
// rule noTwoTripletsAreTheSameVAC(env e, env e2){
//     bytes32 distId1; bytes32 distId2;
//     method f; calldataarg args;
//     address stk1; address dst1; uint256 dur1;
//     address stk2; address dst2; uint256 dur2;
//     storage initial_state = lastStorage;
//     distId1 = createDistribution(e, stk1, dst1, dur1);
//     distId2 = createDistribution(e2, stk2, dst2, dur2);
//     f(e,args);
//     bool exp = ((getStakingToken(distId1) != getStakingToken(distId2)) || (getDistributionToken(distId1) != getDistributionToken(distId2)) || (getOwner(distId1) != getOwner(distId2)));
//     bool distNotExist1 = distNotExist(distId1) at initial_state;
//     bool distNotExist2 = distNotExist(distId2);
//     // require distNotExist1 && distNotExist2;
//     assert (distNotExist1 && distNotExist2 => exp, "after calling f");
//    // assert false, "sanity";
// }


/*
rule distributionsAreIndependent(method f, bytes32 distId1, bytes32 distId2){
    env e1; env e2; bytes32[] distIdArray;
    address _sToken = getStakingToken(distId1);
    address _dToken = getDistributionToken(distId1);
    address _owner = getOwner(distId1);
    uint256 _totSupply = getTotalSupply(distId1);
    uint256 _duration = getDuration(distId1);
    uint256 _pFinished = getPeriodFinish(distId1);
    uint256 _pRate = getPaymentRate(distId1);
    uint256 _lastUpdateTime = getLastUpdateTime(distId1);
    uint256 _globalTokensPerStake = getGlobalTokensPerStake(distId1);

    setUp(e2, distId1, _, _, _, _);
    setUp(e2, distId2, _, _, _, _);

    require distId2 != distId1;
    require distIdArray.length <= 1 && distIdArray[0] != distId1;
    callAllFunctionsWithParameters(f, e2, distId2, distIdArray);

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
    assert ((totSupply_ == _totSupply) || ), "totSupply changed";
    assert duration_ == _duration, "duration changed";
    assert pFinished_ == _pFinished, "period finished changed";
    assert pRate_ == _pRate, "payment rate changed";
    assert ((lastUpdateTime_ == _lastUpdateTime) || )=> , "last update time changed";
    assert ((globalTokensPerStake_ == _globalTokensPerStake) || )=>, "global Tokens Per Stake changed";
}
*/

// globalTokensPerStake is non-decreasing 
rule gtpsMonotonicity(bytes32 distributionId, method f){
        uint256 gtpsBefore = getGlobalTokensPerStake(distributionId);

        env e;
        calldataarg args;
        f(e, args);

        uint256 gtpsAfter = getGlobalTokensPerStake(distributionId);

        assert gtpsBefore <= gtpsAfter, "gtps was decreased";
}


// userTokensPerStake is non-decreasing 
rule utpsMonotonicity(bytes32 distributionId, method f, address stakingToken, address user, uint256 index){
        requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distributionId);
        requireInvariant globalGreaterOrEqualUser(distributionId, stakingToken, user);

        uint256 utpsBefore = getUserTokensPerStake(distributionId, stakingToken, user);
        uint256 gtpsBefore = getGlobalTokensPerStake(distributionId);

        env e;
        calldataarg args;
        f(e, args);

        uint256 utpsAfter = getUserTokensPerStake(distributionId, stakingToken, user);
        uint256 gtpsAfter = getGlobalTokensPerStake(distributionId);

        assert utpsBefore <= utpsAfter, "utps was decreased";
}


// lastUpdateTime is non-decreasing 
rule lastUpdateTimeMonotonicity(bytes32 distributionId, method f, address stakingToken, address sender){
        env e;
        
        requireInvariant lastUpdateTimeNotInFuture(e, distributionId);
        require !distNotExist(distributionId);
        requireInvariant getLastUpdateTimeLessThanFinish(distributionId);

        uint256 lastUpdateTimeBefore = getLastUpdateTime(distributionId);

        calldataarg args;
        f(e, args);

        uint256 lastUpdateTimeAfter = getLastUpdateTime(distributionId);

        assert lastUpdateTimeBefore <= lastUpdateTimeAfter, "lastUpdateTime was decreased";
}


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


// Check that the changes to total supply are coherent with the changes to balance
rule integrityBalanceOfTotalSupply(address userA, address stakingToken, bytes32 distributionId, method f, uint256 index) {
    env e; 
    
    require e.msg.sender == userA;
    require getStakingToken(distributionId) == stakingToken;
    requireInvariant enumerableSetIsCorrelated(stakingToken, userA, index, distributionId);
    requireInvariant userSubStakeCorrelationWithTotalSupply(distributionId, userA, stakingToken, index, e);
    
	uint256 balanceABefore = getUserBalance(stakingToken, userA);
	uint256 totalSupplyBefore = getTotalSupply(distributionId);

	calldataarg args;
    f(e, args); 

	uint256 balanceAAfter = getUserBalance(stakingToken, userA);
	uint256 totalSupplyAfter = getTotalSupply(distributionId);

	assert (balanceAAfter != balanceABefore) 
                => (balanceAAfter - balanceABefore  == totalSupplyAfter - totalSupplyBefore), "not correlated";
}


// can a durtion be changed if distribution is active
rule unchangedDurationDuringActiveDistribution(bytes32 distributionId, method f){
    env e;

    require distActive(distributionId, e);

    uint256 durationBefore = getDuration(distributionId);

    calldataarg args;
    f(e, args);

    uint256 durationAfter = getDuration(distributionId);

    assert durationBefore == durationAfter;
}


rule permanentOwner(bytes32 distributionId, method f){
    env e;
    
    require distNew(distributionId) || distActive(distributionId, e) || distFinished(distributionId, e);

    address ownerBefore = getOwner(distributionId);

    calldataarg args;
    f(e, args);

    address ownerAfter = getOwner(distributionId);

    assert ownerAfter == ownerBefore;
}


rule claimCheck(address stToken, address dstToken, address user, bytes32 distributionId, uint256 index){
    env e;
    
    require isSubscribed(distributionId, user);
    require getStakingToken(distributionId) == stToken;
    require getDistributionToken(distributionId) == dstToken;
    requireInvariant enumerableSetIsCorrelated(stToken, user, index, distributionId);
    require getUserBalance(stToken, user) > 0;
    require distributionId > 0;
    require stToken > 0;

    bytes32[] distributionIds;
    require distributionIds.length == 1;
    require distributionIds[0] == distributionId;
    bool toInternalBalance;
    address sender;
    
    uint256 assetBefore; uint256 internalBefore; uint256 taouBefore;
    uint256 assetAfter; uint256 internalAfter; uint256 taouAfter;

    assetBefore, internalBefore, taouBefore = Vault.totalAssetsOfUser(e, dstToken, user);

    uint256 shouldBeClaimedAfter = getClaimableTokens(e, distributionId, sender);

    claim(e, distributionIds, toInternalBalance, sender, user);

    uint256 userBalance = getUserBalance(stToken, user);

    assetAfter, internalAfter, taouAfter = Vault.totalAssetsOfUser(e, dstToken, user);

    mathint all = taouBefore + shouldBeClaimedAfter;

    assert all == to_mathint(taouAfter), "total asssets are not the same";
}

// asset as getUnclaimedTokens
// check that claim increases assets
// check that assets are incresed by getClaimeableTokens of 

rule itIsOnlyMyReward(address stToken, address dstToken, bytes32 distributionId, uint256 index, address sender){
    env e;
    address userA; address userB;
    require isSubscribed(distributionId, sender); require isSubscribed(distributionId, userB);
    requireInvariant enumerableSetIsCorrelated(stToken, sender, index, distributionId); requireInvariant enumerableSetIsCorrelated(stToken, userB, index, distributionId);
    requireInvariant userSubStakeCorrelationWithTotalSupply(distributionId, userA, stToken, index, e); requireInvariant userSubStakeCorrelationWithTotalSupply(distributionId, userB, stToken, index, e);

    require getStakingToken(distributionId) == stToken;
    require getDistributionToken(distributionId) == dstToken;

    bytes32[] distributionIds;
    require distributionIds.length == 1;
    require distributionIds[0] == distributionId;
    bool toInternalBalance;

    uint256 userBShouldClaimBefore = getClaimableTokens(e, distributionId, userB);

    claim(e, distributionIds, toInternalBalance, sender, userA);

    uint256 userBShouldClaimAfter = getClaimableTokens(e, distributionId, userB);

    assert userBShouldClaimBefore <= userBShouldClaimAfter;

}



/////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////    Ghost    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////
/*
ghost userSubscribed(address, address, bytes32) returns bool {
	init_state axiom forall address token. forall address user. forall bytes32 distributionId. userSubscribed(token, user, distributionId) == false;
}

hook Sstore userSubscriptions[KEY address token][KEY address user][KEY bytes32 distributionId] bool isSub STORAGE{
    havoc userSubscribed assuming forall address stToken. forall address userAddr. forall bytes32 distId. (stToken == token && userAddr == user && distId == distributionId
                                                => userSubscribed@new(stToken, userAddr, distId) == isSub)
                                                && (stToken != token || userAddr != user || distId != distributionId
                                                        => userSubscribed@new(stToken, userAddr, distId) == userSubscribed@old(stToken, userAddr, distId));
    //havoc balanceOfAllUsersInDistribution assuming forall distId. distId == distributionId && isSub => update by adding balancce of a user balanceOfAllUsersInDistribution(distributionId)
}


ghost balanceOfAllUsersInDistribution(bytes32) returns uint256 {
	init_state axiom forall bytes32 distributionId. balanceOfAllUsersInDistribution(distributionId) == 0;
}

hook Sstore _userStakings[KEY address token][KEY address user].balance uint256 userBalance(uint256 old_userBalance) STORAGE {
	havoc balanceOfAllUsersInDistribution assuming forall bytes32 distributionId. userSubscribed(token, user, distributionId) == true
                        => balanceOfAllUsersInDistribution@new(distributionId) == balanceOfAllUsersInDistribution@old(distributionId) + userBalance - old_userBalance 
                        && userSubscribed(token, user, distributionId) == false
                            => balanceOfAllUsersInDistribution@new(distributionId) == balanceOfAllUsersInDistribution@old(distributionId);
}
*/


// totalSupply == sum( (users staked and subscribed).balance )
// invariant totalEqualSumAll(bytes32 distributionId)
//     getTotalSupply(distributionId) == balanceOfAllUsersInDistribution(distributionId)

// https://vaas-stg.certora.com/output/3106/c55d5aa7f101fae01655/?anonymousKey=4179fa9da86b0e3d07c78e48f6e48776b8470ec9
// subscribeDistributions() - updates in userSubscribed() should force updates in balanceOfAllUsersInDistribution()
// unsubscribeDistributions() - wrong initial state when totalSupply = 0 but user subscribed and staked, need invariant for it
// stake() - wrong update of a ghost, when we call stake, we call it for a stakingToken but not for a spesific distributionId. That's why update can be wrong
// unstake() - wrong update of a ghost, when we call unstake, we call it for a stakingToken but not for a spesific distributionId. That's why update can be wrong

