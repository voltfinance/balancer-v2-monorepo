methods {
    // getters for view functions
    getScheduledDistributionId(bytes32) returns bytes32 envfree
    getScheduledStartTime(bytes32) returns uint256 envfree
    getScheduledAmount(bytes32) returns uint256 envfree
    getScheduledStatus(bytes32) returns uint8 envfree //enum

    // non view functions
    getScheduleId(bytes32, uint256) returns bytes32 envfree
    // scheduleDistribution(bytes32, uint256, uint256) returns bytes32
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

invariant scheduleExistInitializedParams(bytes32 scheduleId)
        (getScheduledDistributionId(scheduleId) == 0 <=> getScheduledStartTime(scheduleId) == 0) &&
        (getScheduledStartTime(scheduleId) == 0 <=> getScheduledAmount(scheduleId) == 0) &&
        (getScheduledAmount(scheduleId) == 0 <=> getScheduledStatus(scheduleId) == 0)

