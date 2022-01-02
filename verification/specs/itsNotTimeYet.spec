/////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////    MultiDistributor    //////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////



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

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Scheduler    //////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////


// F@F - starting from an initial state where dist 1 & 2 does not exist (all fields are in default values),
// creation of 2 dists (with different ids) must result from 2 different trios. 
// @note that hashUniquness is assuming that for different distIds the trios are not equal,
// therefore the rule is basically weaker than intended, it mainly shows that createDistribution from DistNotExist
// populate the mapping with the distinct trios
rule noTwoDuosAreTheSameFirstStep(env e, env e2, bytes32 scheduleId1, bytes32 scheduleId2){
    method f; calldataarg args;
    bytes32 distId1; uint256 amount1; uint256 startTime1;
    bytes32 distId2; uint256 amount2; uint256 startTime2;

    require (distScheduleNotExist(scheduleId1) && distScheduleNotExist(scheduleId2));
    bytes32 scheduleId1_return = scheduleDistribution(e, distId1, amount1, startTime1);
    bytes32 scheduleId2_return = scheduleDistribution(e2, distId2, amount2, startTime2);
 
    // hashUniquness(scheduleId1_return, distId1, startTime1, scheduleId2_return, distId2, startTime2);
    requireScheduleIdCorrelatedWithDuo(scheduleId1_return, distId1, startTime1); requireInvariant scheduleExistInitializedParams(scheduleId1);
    requireScheduleIdCorrelatedWithDuo(scheduleId2_return, distId2, startTime2); requireInvariant scheduleExistInitializedParams(scheduleId2);

    assert ((scheduleId1 == scheduleId1_return && scheduleId2 == scheduleId2_return) => 
            ((getScheduledDistributionId(scheduleId1_return) != getScheduledDistributionId(scheduleId2_return)) || 
            (getScheduledStartTime(scheduleId1_return) != getScheduledStartTime(scheduleId2_return))));
}


// V@V - Once 2 distributions has 2 distinct trios constituting them, their trio fields cannot be changed in such a way that will make them equivalent.
rule noTwoDuosAreTheSame(env e, bytes32 scheduleId1, bytes32 scheduleId2){
    method f; calldataarg args;
    bytes32 distId1; uint256 amount1; uint256 startTime1;
    bytes32 distId2; uint256 amount2; uint256 startTime2;

    require (!distScheduleNotExist(scheduleId1) && !distScheduleNotExist(scheduleId2));
    requireInvariant oneScheduleStateAtATime(scheduleId1, e); requireInvariant oneScheduleStateAtATime(scheduleId2, e);
    requireScheduleIdCorrelatedWithDuo(scheduleId1, distId1, startTime1); requireInvariant scheduleExistInitializedParams(scheduleId1);
    requireScheduleIdCorrelatedWithDuo(scheduleId2, distId2, startTime2); requireInvariant scheduleExistInitializedParams(scheduleId2);
    require ((getScheduledDistributionId(scheduleId1) != getScheduledDistributionId(scheduleId2)) || (getScheduledStartTime(scheduleId1) != getScheduledStartTime(scheduleId2)));
    f(e,args);
    assert ((getScheduledDistributionId(scheduleId1) != getScheduledDistributionId(scheduleId2)) || (getScheduledStartTime(scheduleId1) != getScheduledStartTime(scheduleId2))), "both fields are the same";
}


//  State transition: UNINITIALIZED -> PENDING
rule transition_DistScheduleNotExist_To_DistScheduleCreated(bytes32 scheduleId, method f) filtered { f -> f.selector != certorafallback_0().selector } {
    env e; calldataarg args;
    require distScheduleNotExist(scheduleId);
    
    stateTransitionHelper(f, e, scheduleId);

    assert f.selector != scheduleDistribution(bytes32, uint256, uint256).selector <=> distScheduleNotExist(scheduleId), "schedule changed state without scheduling a distribution";
    assert f.selector == scheduleDistribution(bytes32, uint256, uint256).selector <=> distScheduleCreated(scheduleId, e), "schedule did not change due to call to scheduleDistribution function";
}


// State transition: PENDING -> STARTED
//                   PENDING -> CANCELLED
rule transition_DistScheduleCreated_To_DistStarted_Or_DistCancelled(bytes32 scheduleId, method f) filtered { f -> f.selector != certorafallback_0().selector } {
    env e; calldataarg args;
    require distScheduleCreated(scheduleId, e);
    
    stateTransitionHelper(f, e, scheduleId);

    assert !lastReverted 
                => ((f.selector != startDistributions(bytes32[]).selector && f.selector != cancelDistribution(bytes32).selector) 
                            <=> distScheduleCreated(scheduleId, e)), "schedule changed state without starting a distribution";
    assert f.selector == startDistributions(bytes32[]).selector <=> distStarted(scheduleId, e), "schedule did not change due to call to startDistributions function";
    assert f.selector == cancelDistribution(bytes32).selector <=> distCancelled(scheduleId, e), "schedule did not change due to call to cancelDistribution function";
}
