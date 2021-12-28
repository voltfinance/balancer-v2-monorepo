methods {
    // getters for view functions
    getScheduledDistributionId(bytes32) returns bytes32 envfree
    getScheduledStartTime(bytes32) returns uint256 envfree
    getScheduledAmount(bytes32) returns uint256 envfree
    getScheduledStatus(bytes32) returns uint8 envfree //enum

    // non view functions
    getScheduleId(bytes32, uint256) returns bytes32 envfree
    scheduleDistribution(bytes32, uint256, uint256) returns bytes32
    startDistributions(bytes32[])
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
//////////////////////////////////////    Helpers    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

function requireEnvValuesNotZero(env e){
    require e.msg.sender != 0;
    require e.block.number != 0;
    require e.block.timestamp != 0;
}

// assuming the hash is deterministic, and correlates the arg duo properly
function requireScheduleIdCorrelatedWithDuo(bytes32 scheduleId, bytes32 _distId, uint256 _startTime){
    // given 2 arbitrary args, the hashing function should retrieve the value scheduleId.
    // also the distId and startTime associated with this scheduleId must match the arbitrary values.
    require (getScheduleId(_distId, _startTime) == scheduleId && (getScheduledDistributionId(scheduleId) == _distId && getScheduledStartTime(scheduleId) == _startTime));
}

/////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////    Michael    ///////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// V@V - distributionId, startTime, amount are either initialized (!=0) or uninitialized (0) simultaneously
invariant scheduleExistInitializedParams(bytes32 scheduleId)
        (getScheduledDistributionId(scheduleId) == 0 <=> getScheduledStartTime(scheduleId) == 0) &&
        (getScheduledStartTime(scheduleId) == 0 <=> getScheduledAmount(scheduleId) == 0) &&
        (getScheduledAmount(scheduleId) == 0 <=> getScheduledStatus(scheduleId) == 0)
            filtered { f -> f.selector != certorafallback_0().selector }


// F@F - fails on certoraFall back in preserved block - If duration/owner/staking_token/distribution_token are not set, the distribution does not exist
invariant conditionsScheduleNotExist(bytes32 scheduleId)
        getScheduledStatus(scheduleId) == 0 <=> distScheduleNotExist(scheduleId)
            filtered { f -> f.selector != certorafallback_0().selector }


// The system is in either of the 4 defined states. It cannot be in any other state, nor in more than 1 state at the same time.
invariant oneStateAtATime(bytes32 scheduleId, env e)
        ((distScheduleNotExist(scheduleId) && !distScheduleCreated(scheduleId, e) && !distStarted(scheduleId, e) && !distCancelled(scheduleId, e)) ||
        (!distScheduleNotExist(scheduleId) && distScheduleCreated(scheduleId, e) && !distStarted(scheduleId, e) && !distCancelled(scheduleId, e)) ||
        (!distScheduleNotExist(scheduleId) && !distScheduleCreated(scheduleId, e) && distStarted(scheduleId, e) && !distCancelled(scheduleId, e)) ||
        (!distScheduleNotExist(scheduleId) && !distScheduleCreated(scheduleId, e) && !distStarted(scheduleId, e) && distCancelled(scheduleId, e)))
            filtered { f -> f.selector != certorafallback_0().selector }


invariant scheduleForFuture(bytes32 scheduleId, env e)
        distScheduleCreated(scheduleId, e) => getScheduledStartTime(scheduleId) < e.block.timestamp
            filtered { f -> f.selector != certorafallback_0().selector }
        { 
            preserved with (env e2)
            { 
                require e.block.timestamp == e2.block.timestamp;
            }
        }


// if canceled cannot do anything
// strange scenarious
rule noLifeAfterCancellation(bytes32 scheduleId, env e, method f) filtered { f -> f.selector != certorafallback_0().selector } {
    bytes32[] scheduleIds;
    uint256 amount; uint256 startTime;

    require distCancelled(scheduleId, e);
    require scheduleIds.length == 3;
    require scheduleIds[0] == scheduleId;

    calldataarg args;
    invoke f(e, args);

    assert !lastReverted, "something happened";
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


// can non owner get distribution money --- will require multicontracts and I'm not sure if it makes sense