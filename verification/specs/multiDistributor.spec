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
    getUserBalance(address, address) returns uint256 envfree

    // view functions
    isSubscribed(bytes32, address) returns bool envfree
    IsSubscribedFull(address, address, bytes32) returns bool envfree

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

function requireEnvValuesNotZero(env e){
    require e.msg.sender != 0;
    require e.block.number != 0;
    require e.block.timestamp != 0;
}

function callCreateDistributionWithSpecificDistId(method f, env e, bytes32 distId){
    address stakingToken; address distributionToken; uint256 duration;
    if (f.selector == createDistribution(address, address, uint256).selector) {
        bytes32 distributionId = createDistribution(e, stakingToken, distributionToken, duration);
        require distributionId == distId;
    } else {
        calldataarg args;
        f(e, args);
    }
}

function callFundDistributionWithSpecificDistId(method f, env e, bytes32 distId){
    uint256 amount;
    if (f.selector == fundDistribution(bytes32, uint256).selector) {
        fundDistribution(e, distId, amount);
    } else {
        calldataarg args;
        f(e, args);
    }
}
/*
function callAllFunctionsWithParameters(method f, env e, bytes32 distributionId, address recipient){
    address stakingToken; address distributionToken; uint256 duration; uint256 amount;
    bytes32[] distributionIds; address sender; uint256 deadline; uint8 v; bytes32 r; bytes32 s;
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
	} else if  (f.selector == stakeWithPermit(address, uint256, address, uint256, uint8, bytes32, bytes32).selector) {
        stakeWithPermit(e, stakingToken, amount, recipient, deadline, v, r, s);
	} else if (f.selector == unstake(address, uint256, address, address).selector) {
		unstake(e, stakingToken, amount, sender, recipient);
    } else if (f.selector == claim(bytes32[], bool, address, address).selector) {
        claim(e, distributionIds, toInternalBalance, sender, recipient);
    } else if (f.selector == claimWithCallback(bytes32[], address, address, bytes).selector) {
        claimWithCallback(e, distributionIds, sender, callbackContract,callbackData);
	} else if  (f.selector == exit(address[], bytes32[]).selector) {
        exit(e, stakingTokens, distributionIds);
	} else if (f.selector == exitWithCallback(address[], bytes32[], address, bytes).selector) {
		exitWithCallback(e, stakingTokens, distributionIds, callbackContract, callbackData);
	} else {
        calldataarg args;
        f(e, args);
    }
}
*/

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


// V@V - A user cannot be subscribed to a distribution that does not exist, and the other way around - if a user is subscribed to a distribution then it has to exist
invariant notSubscribedToNonExistingDist(bytes32 distId, address user)
        (getStakingToken(distId) == 0 => !isSubscribed(distId, user)) &&
            (isSubscribed(distId, user) => getStakingToken(distId) != 0)
        {
            preserved unsubscribeDistributions(bytes32[] distributionIdArray) with (env e)
            {
                address stakingToken; uint256 index;
                requireInvariant enumerableSetIsCorrelated(stakingToken, user, index, distId);
            }
        }


// F@F - fail on STAKE. If duration/owner/staking_token/distribution_token are not set, the distribution does not exist
// @note that unit256 index is an arbitrary value. it is defined as an arg to the invariant merely so it could be used in all preserved block at once.
invariant conditionsDistNotExist(bytes32 distId/*, uint256 index*/)
        getStakingToken(distId) == 0 => distNotExist(distId)
        {
            preserved stake(address stakingToken, uint256 amount, address sender, address recipient) with (env e)
            {
                require getStakingToken(distId) == stakingToken;
                requireInvariant enumerableSetIsCorrelated(stakingToken, recipient, index, distId);
                requireInvariant notSubscribedToNonExistingDist(distId, recipient);
            }
            // preserved stakeUsingVault(address stakingToken, uint256 amount, address sender, address recipient) with (env e)
            // {
            //     require getStakingToken(distId) == stakingToken;
            //     requireInvariant enumerableSetIsCorrelated(stakingToken, recipient, index, distId);
            //     requireInvariant notSubscribedToNonExistingDist(distId, recipient);
            // }
            // preserved stakeWithPermit(address stakingToken, uint256 amount, address user, uint256 deadline, uint8 v, bytes32 r, bytes32 s) with (env e)
            // {
            //     require getStakingToken(distId) == stakingToken;
            //     requireInvariant enumerableSetIsCorrelated(stakingToken, recipient, index, distId);
            //     requireInvariant notSubscribedToNonExistingDist(distId, recipient);
            // }
            // preserved unstake(address stakingToken, uint256 amount, address sender, address recipient) with (env e)
            // {
            //     require getStakingToken(distId) == stakingToken;
            //     requireInvariant enumerableSetIsCorrelated(stakingToken, recipient, index, distId);
            //     requireInvariant notSubscribedToNonExistingDist(distId, recipient);
            // }
            // preserved exit(address[] stakingTokens, bytes32[] distributionIds) with (env e)
            // {
            //     require getStakingToken(distId) == stakingTokens[0];
            //     requireInvariant enumerableSetIsCorrelated(stakingToken, recipient, index, distId);
            //     requireInvariant notSubscribedToNonExistingDist(distId, recipient);
            // }
            // preserved exitWithCallback(address[] stakingTokens, bytes32[] distributionIds, address callbackContract, bytes callbackData) with (env e)
            // {
            //     require getStakingToken(distId) == stakingTokens[0];
            //     requireInvariant enumerableSetIsCorrelated(stakingToken, recipient, index, distId);
            //     requireInvariant notSubscribedToNonExistingDist(distId, recipient);
            // }
            
        }


// F@F - fails on many functions. will pass once conditionsDistNotExist will pass
// Creating a dist bringing us from the state distNotExist to distNew (no other function does that). All other functions will leave us in distNotExist state.
// @note that we dont check createDistribution for a distribution_ID != distId, assuming that any operation on other dists will not effect this one.
rule transition_NotExist_To_DistNew(bytes32 distId) {
    method f; env e; calldataarg args;
    require distNotExist(distId);
    requireEnvValuesNotZero(e);
    
    // calling all functions, making sure the created distribution id is the distId of interest
    callCreateDistributionWithSpecificDistId(f, e, distId);
    assert f.selector != createDistribution(address, address, uint256).selector => distNotExist(distId), "distribution changed state without creating a distribution";
    assert f.selector == createDistribution(address, address, uint256).selector => distNew(distId), "distribution did not change due to call to createDistribution function";
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


// V@V - Funding a dist bringing us from the state distNew to distActive (no other function does that). All other functions will leave us in distNew state.
rule transition_DistNew_To_DistActive(bytes32 distId){
    method f; env e; calldataarg args;
    require distNew(distId);
    requireEnvValuesNotZero(e);
    
    // calling all functions, making sure the created distribution id is the distId of interest
    callFundDistributionWithSpecificDistId(f, e, distId);
    assert f.selector != fundDistribution(bytes32, uint256).selector => distNew(distId), "distribution changed state without funding a distribution";
    assert f.selector == fundDistribution(bytes32, uint256).selector => distActive(distId, e), "distribution did not change due to call to fundDistribution function";
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


// V@V - All function calls will leave us in distActive state. only time can change a dist state to finished.
// @note that the require on e2 is being done after the function call. 
// If we'll move it anywhere before the function call the prover will fail on fundDistribution, which extend the active period.
// This way we simulate elapsing time with gurantee to get timestamp that exceed the periodFinished timestamp.
rule transition_DistActive_To_DistFinished(bytes32 distId){
    method f;  env e; calldataarg args; env e2;
    require distActive(distId, e);
    requireEnvValuesNotZero(e);
    require e2.msg.sender == e.msg.sender;

    f(e, args);

    require e2.block.timestamp > getPeriodFinish(distId);
    // require e.block.timestamp > getPeriodFinish(distId);

    assert distActive(distId, e), "distribution changed state";
    assert distFinished(distId, e2), "distribution did not change state to finished even though the finish date has arrived";
}


// V@V - Funding a dist bringing us from the state distFinished back to distActive (no other function does that). All other functions will leave us in distFinished state.
rule transition_DistFinished_To_DistActive(bytes32 distId){
    method f; env e; calldataarg args;
    require distFinished(distId, e);
    requireEnvValuesNotZero(e);
    
    // calling all functions, making sure the created distribution id is the distId of interest
    callFundDistributionWithSpecificDistId(f, e, distId);
    assert f.selector != fundDistribution(bytes32, uint256).selector => distFinished(distId, e), "distribution changed state without funding a distribution";
    assert f.selector == fundDistribution(bytes32, uint256).selector => distActive(distId, e), "distribution did not change due to call to fundDistribution function";
}


// F@F - fails on account of total supply != 0.
// The system is in either of the 4 defined states. It cannot be in any other state, nor in more than 1 state at the same time.
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
                requireInvariant distExistInitializedParams(distId, e2);
                requireInvariant distActivatedAtLeastOnceParams(distId, e2);
            }
        }


// V@V - The global reward token per stake token var is always greater or equal to the user's reward token per stake token 
invariant globalGreaterOrEqualUser(bytes32 distributionId, address stakingToken, address sender)
        getGlobalTokensPerStake(distributionId) >= getUserTokensPerStake(distributionId, stakingToken, sender)


/////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////    Rules    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

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

// lastUpdateTime can't be in the future
invariant lastUpdateTimeNotInFuture(env e, bytes32 distributionId)
    getLastUpdateTime(distributionId) <= e.block.timestamp
    {preserved with (env e2)
    {
        require e.block.timestamp == e2.block.timestamp;
    }}


// lastUpdateTime cannot be greater than periodFinish
invariant getLastUpdateTimeLessThanFinish(bytes32 distributionId)
    getLastUpdateTime(distributionId) <= getPeriodFinish(distributionId)



/////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////    Ghost    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

ghost userSubscribed(address, address, bytes32) returns bool {
	init_state axiom forall address token. forall address user. forall bytes32 distributionId. userSubscribed(token, user, distributionId) == false;
}

hook Sstore userSubscriptions[KEY address token][KEY address user][KEY bytes32 distributionId] bool isSub STORAGE{
    havoc userSubscribed assuming forall address stToken. forall address userAddr. forall bytes32 distId. (stToken == token && userAddr == user && distId == distributionId
                                                => userSubscribed@new(stToken, userAddr, distId) == isSub)
                                                && (stToken != token && userAddr != user && distId != distributionId
                                                        => userSubscribed@new(stToken, userAddr, distId) == userSubscribed@old(stToken, userAddr, distId));
}

ghost balanceOfAllUsersInDistribution(bytes32) returns uint256 {
	init_state axiom forall bytes32 distributionId. balanceOfAllUsersInDistribution(distributionId) == 0;
}

hook Sstore _userStakings[KEY address token][KEY address user].balance uint256 userBalance(uint256 old_userBalance) STORAGE {
	havoc balanceOfAllUsersInDistribution assuming forall bytes32 distributionId. userSubscribed(token, user, distributionId) == true
                                                => balanceOfAllUsersInDistribution@new(distributionId) == balanceOfAllUsersInDistribution@old(distributionId) + userBalance - old_userBalance;
}


// totalSupply == sum( (users staked and subscribed).balance )
invariant totalEqualSumAll(bytes32 distributionId)
    getTotalSupply(distributionId) == balanceOfAllUsersInDistribution(distributionId)

// https://vaas-stg.certora.com/output/3106/c55d5aa7f101fae01655/?anonymousKey=4179fa9da86b0e3d07c78e48f6e48776b8470ec9
// subscribeDistributions() - updates in userSubscribed() should force updates in balanceOfAllUsersInDistribution()
// unsubscribeDistributions() - wrong initial state when totalSupply = 0 but user subscribed and staked, need invariant for it
// stake() - wrong update of a ghost, when we call stake, we call it for a stakingToken but not for a spesific distributionId. That's why update can be wrong
// unstake() - wrong update of a ghost, when we call unstake, we call it for a stakingToken but not for a spesific distributionId. That's why update can be wrong


invariant userSubStakeCorrelationWithTotalSupply(bytes32 distributionId, address user, address token)
    isSubscribed(distributionId, user) && getStakingToken(distributionId) == token => getUserBalance(token, user) <= getTotalSupply(distributionId)
    { preserved {
        requireInvariant notSubscribedToNonExistingDist(distributionId, user);
    }}


// the amount of claimed tokens is less or equal to the amount of possible reward of all subscribed and staked users