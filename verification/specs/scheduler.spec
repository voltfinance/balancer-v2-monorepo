methods {
    // getters for view functions
    getScheduledDistributionId(bytes32) returns bytes32 envfree
    getScheduledStartTime(bytes32) returns uint256 envfree
    getScheduledAmount(bytes32) returns uint256 envfree
    getScheduledStatus(bytes32) returns uint8 envfree //enum

    // non view functions
    getScheduleId(bytes32 distributionId, uint256 startTime) returns bytes32 envfree => uniqueHashGhost(distributionId, startTime)
    scheduleDistribution(bytes32, uint256, uint256) returns bytes32
    startDistributions(bytes32[])
    cancelDistribution(bytes32)

    balanceOf(address) returns uint256 => DISPATCHER(true)
    transfer(address, uint256) returns bool => DISPATCHER(true)
    transferFrom(address, address, uint256) returns bool => DISPATCHER(true)
    approve(address, uint256) returns (bool) => DISPATCHER(true)
}

/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////    Definitions    /////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// Schedule Not Exist - all parameters are set to default values.
definition distScheduleNotExist(bytes32 scheduleId) returns bool =
    getScheduledDistributionId(scheduleId) == 0 &&
    getScheduledStartTime(scheduleId) == 0 &&
    getScheduledAmount(scheduleId) == 0 &&
    getScheduledStatus(scheduleId) == 0;


// schedule Created, the distribution scheduled but not yet started - 3 parameters are non-zero, status == 1.
definition distScheduleCreated(bytes32 scheduleId, env e) returns bool =
    getScheduledDistributionId(scheduleId) != 0 &&
    (getScheduledStartTime(scheduleId) != 0 && getScheduledStartTime(scheduleId) > e.block.timestamp) &&
    getScheduledStatus(scheduleId) == 1;


// Distribution Started, the scheduled distribution started - 3 parameters are non-zero, status == 2.
definition distStarted(bytes32 scheduleId, env e) returns bool =
    getScheduledDistributionId(scheduleId) != 0 &&
    (getScheduledStartTime(scheduleId) != 0 && getScheduledStartTime(scheduleId) <= e.block.timestamp) &&
    getScheduledStatus(scheduleId) == 2;


// Distribution Started, the scheduled distribution started - 3 parameters are non-zero, status == 2.
definition distCancelled(bytes32 scheduleId, env e) returns bool =
    getScheduledDistributionId(scheduleId) != 0 &&
    (getScheduledStartTime(scheduleId) != 0 && getScheduledStartTime(scheduleId) > e.block.timestamp) &&
    getScheduledStatus(scheduleId) == 3;

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Ghost    //////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// Ghost that keeps track of the hashing to assume determinism of the hashing operation.
ghost uniqueHashGhost(bytes32, uint256) returns bytes32;

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Helpers    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// Making sure the env does not take any 0 values which aren't realistic anyway
function requireEnvValuesNotZero(env e){
    require e.msg.sender != 0;
    require e.block.number != 0;
    require e.block.timestamp != 0;
}

// Assuming the hash is deterministic, and correlates the arg duo properly
function requireScheduleIdCorrelatedWithDuo(bytes32 scheduleId, bytes32 _distId, uint256 _startTime){
    // given 2 arbitrary args, the hashing function should retrieve the value scheduleId.
    // also the distId and startTime associated with this scheduleId must match the arbitrary values.
    require (getScheduleId(_distId, _startTime) == scheduleId && (getScheduledDistributionId(scheduleId) == _distId && getScheduledStartTime(scheduleId) == _startTime));
}

// Assuming the hash is deterministic, and correlates the duo properly
function hashUniquness(bytes32 scheduleId1, bytes32 distId1, uint256 startTime1, bytes32 scheduleId2, bytes32 distId2, uint256 startTime2){
    require (((distId1 != distId2) || (startTime1 != startTime2)) <=> 
    (uniqueHashGhost(distId1, startTime1) != uniqueHashGhost(distId2, startTime2)));
}

// Calling all non-view function with specified parameters.
// A helper function that allows modification of the input args to assure specific values are being passed to the contract's functions when needed
function callAllFunctionsWithParameters(method f, env e, bytes32 scheduleId, bytes32[] scheduleIds){
    bytes32 distId; uint256 startTime; uint256 amount;
    if (f.selector == scheduleDistribution(bytes32, uint256, uint256).selector) {
        bytes32 schedId = scheduleDistribution(e, distId, amount, startTime);
        require schedId == scheduleId;
	} else if (f.selector == startDistributions(bytes32[]).selector) {
        startDistributions(e, scheduleIds);
	} else if (f.selector == cancelDistribution(bytes32).selector) {
		cancelDistribution(e, scheduleId);
    } else {
        calldataarg args;
        f(e, args);
    }
}

function stateTransitionHelper(method f, env e, bytes32 scheduleId){
    bytes32 distributionId; uint256 amount; uint256 startTime;
    bytes32[] scheduleIds;

	if (f.selector == scheduleDistribution(bytes32, uint256, uint256).selector) {
        bytes32 schID = scheduleDistribution(e, distributionId, amount, startTime);
        require schID == scheduleId;
	} else if (f.selector == startDistributions(bytes32[]).selector) {
        require scheduleIds.length > 0;
        require scheduleIds[0] == scheduleId;
        startDistributions(e, scheduleIds);
	} else if (f.selector == cancelDistribution(bytes32).selector) {
		cancelDistribution(e, scheduleId);
	} else {
        calldataarg args;
        f(e, args);
    }
}

/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////    Invariants    //////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////


// V@V - distributionId, startTime, amount are either initialized (!=0) or uninitialized (0) simultaneously
invariant scheduleExistInitializedParams(bytes32 scheduleId)
        (getScheduledDistributionId(scheduleId) == 0 <=> getScheduledStartTime(scheduleId) == 0) &&
        (getScheduledStartTime(scheduleId) == 0 <=> getScheduledAmount(scheduleId) == 0) &&
        (getScheduledAmount(scheduleId) == 0 <=> getScheduledStatus(scheduleId) == 0)
            filtered { f -> f.selector != certorafallback_0().selector }


// V@V - If duration/owner/staking_token/distribution_token are not set, the distribution does not exist
invariant conditionsScheduleNotExist(bytes32 scheduleId)
        getScheduledStatus(scheduleId) == 0 <=> distScheduleNotExist(scheduleId)
            filtered { f -> f.selector != certorafallback_0().selector }


// V@V - The system is in either of the 4 defined states. It cannot be in any other state, nor in more than 1 state at the same time.
invariant oneScheduleStateAtATime(bytes32 scheduleId, env e)
        ((distScheduleNotExist(scheduleId) && !distScheduleCreated(scheduleId, e) && !distStarted(scheduleId, e) && !distCancelled(scheduleId, e)) ||
        (!distScheduleNotExist(scheduleId) && distScheduleCreated(scheduleId, e) && !distStarted(scheduleId, e) && !distCancelled(scheduleId, e)) ||
        (!distScheduleNotExist(scheduleId) && !distScheduleCreated(scheduleId, e) && distStarted(scheduleId, e) && !distCancelled(scheduleId, e)) ||
        (!distScheduleNotExist(scheduleId) && !distScheduleCreated(scheduleId, e) && !distStarted(scheduleId, e) && distCancelled(scheduleId, e)))
            filtered { f -> f.selector != certorafallback_0().selector }
        {
            preserved with (env e2)
            {
                require e.block.timestamp == e2.block.timestamp;
            }
        }


/////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////    Rules    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////


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

    assert (f.selector != startDistributions(bytes32[]).selector && f.selector != cancelDistribution(bytes32).selector) <=> distScheduleCreated(scheduleId, e), "schedule changed state without starting a distribution";
    assert f.selector == startDistributions(bytes32[]).selector <=> distStarted(scheduleId, e), "schedule did not change due to call to startDistributions function";
    assert f.selector == cancelDistribution(bytes32).selector <=> distCancelled(scheduleId, e), "schedule did not change due to call to cancelDistribution function";
}


// if started cannot do anything
rule noLifeAfterStart(bytes32 scheduleId, env e, method f) filtered { f -> f.selector != certorafallback_0().selector } {
    // bytes32[] scheduleIds;
    // uint256 amount; uint256 startTime;

    require distStarted(scheduleId, e);

    calldataarg args;
    f(e, args);

    assert distStarted(scheduleId, e), "something happened";
}

// if canceled cannot do anything
rule noLifeAfterCancellation(bytes32 scheduleId, env e, method f) filtered { f -> f.selector != certorafallback_0().selector } {
    // bytes32[] scheduleIds;
    // uint256 amount; uint256 startTime;

    require distCancelled(scheduleId, e);

    calldataarg args;
    f(e, args);

    assert distCancelled(scheduleId, e), "something happened";
}


// once start time and amount are set, they cannot be changed
rule permanentValues(bytes32 scheduleId, env e, method f) filtered { f -> f.selector != certorafallback_0().selector } {
    require distScheduleCreated(scheduleId, e) || distScheduleCreated(scheduleId, e) || distCancelled(scheduleId, e);

    uint256 amountBefore = getScheduledAmount(scheduleId);
    uint256 startTimeBefore = getScheduledStartTime(scheduleId);

    calldataarg args;
    f(e, args);

    uint256 amountAfter = getScheduledAmount(scheduleId);
    uint256 startTimeAfter = getScheduledStartTime(scheduleId);

    assert amountBefore == amountAfter && startTimeBefore == startTimeAfter, "values has changed";
}


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
 
    hashUniquness(scheduleId1_return, distId1, startTime1, scheduleId2_return, distId2, startTime2);
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


// V@V - When calling a function on a specific schedule (start, cancel, and create), no other schedules are being affected
rule schedulesAreIndependent(method f, bytes32 scheduleId1, bytes32 scheduleId2) {
    env e1; env e2; bytes32[] scheduleIdArray;
    bytes32 _distributionId = getScheduledDistributionId(scheduleId1);
    uint256 _startTime = getScheduledStartTime(scheduleId1);
    uint256 _amount = getScheduledAmount(scheduleId1);
    uint8 _status = getScheduledStatus(scheduleId1);

    require scheduleId2 != scheduleId1;
    require scheduleIdArray.length <= 1 && scheduleIdArray[0] != scheduleId1;
    callAllFunctionsWithParameters(f, e2, scheduleId2, scheduleIdArray);

    bytes32 distributionId_ = getScheduledDistributionId(scheduleId1);
    uint256 startTime_ = getScheduledStartTime(scheduleId1);
    uint256 amount_ = getScheduledAmount(scheduleId1);
    uint8 status_ = getScheduledStatus(scheduleId1);

    assert _distributionId == distributionId_, "distribution id changed";
    assert _startTime == startTime_, "start time changed";
    assert _amount == amount_, "amount changed";
    assert _status == status_, "status changed";
    // assert ((totSupply_ == _totSupply) || (nonSpecificDistribution(f) <=> (totSupply_ != _totSupply))), "totSupply changed not due to stake/unstake/exit";
}
