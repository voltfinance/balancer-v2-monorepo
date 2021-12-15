methods {
    // getters for view functions
    getScheduledDistributionId(bytes32) returns bytes32 envfree
    getScheduledStakingToken(bytes32) returns address envfree
    getScheduledDistributionToken(bytes32) returns address envfree
    getScheduledStartTime(bytes32) returns uint256 envfree
    getScheduledOwner(bytes32) returns address envfree
    getScheduledAmount(bytes32) returns uint256 envfree
    getScheduledStatus(bytes32) returns uint8 envfree //enum

    // non view functions
    scheduleDistribution(bytes32, address, address, uint256, uint256) returns bytes32
}

/////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////    Definitions    /////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

// Schedule Not Exist - all parameters are set to default values.
definition distScheduleNotExist(bytes32 scheduleId) returns bool =
    getScheduledDistributionId(scheduleId) == 0 &&
    getScheduledStakingToken(scheduleId) == 0 &&
    getScheduledDistributionToken(scheduleId) == 0 &&
    getScheduledStartTime(scheduleId) == 0 &&
    getScheduledOwner(scheduleId) == 0 &&
    getScheduledAmount(scheduleId) == 0 &&
    getScheduledStatus(scheduleId) == 0;

// schedule Created, the distribution scheduled but not yet started - 4 parameters are non-zero.
definition distScheduleCreated(bytes32 scheduleId) returns bool =
    getScheduledDistributionId(scheduleId) != 0 &&
    getScheduledStakingToken(scheduleId) != 0 &&
    getScheduledDistributionToken(scheduleId) != 0 &&
    getScheduledStartTime(scheduleId) != 0 &&
    getScheduledOwner(scheduleId) != 0 &&
    getScheduledStatus(scheduleId) == 1;

// schedule Created, the distribution scheduled but not yet started - 4 parameters are non-zero.
definition distStarted(bytes32 scheduleId) returns bool =
    getScheduledDistributionId(scheduleId) != 0 &&
    getScheduledStakingToken(scheduleId) != 0 &&
    getScheduledDistributionToken(scheduleId) != 0 &&
    getScheduledStartTime(scheduleId) != 0 &&
    getScheduledOwner(scheduleId) != 0 &&
    getScheduledStatus(scheduleId) == 2;

/////////////////////////////////////////////////////////////////////////////////////////////
//////////////////////////////////////    Helpers    ////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

function requireEnvValuesNotZero(env e){
    require e.msg.sender != 0;
    require e.block.number != 0;
    require e.block.timestamp != 0;
}

function callScheduleDistributionWithSpecificDistId(method f, env e, bytes32 scheduleId){
    bytes32 distId; address stakingToken; address distributionToken; uint256 amount; uint256 startTime;
    if (f.selector == scheduleDistribution(bytes32, address, address, uint256, uint256).selector) {
        bytes32 schedId = scheduleDistribution(e, distId, stakingToken, distributionToken, amount, startTime);
        require schedId == scheduleId;
    } else {
        calldataarg args;
        f(e, args);
    }
}

/////////////////////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////    Michael    ///////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////

invariant scheduleExistInitializedParams(bytes32 scheduleId)
        (getScheduledDistributionId(scheduleId) == 0 <=> getScheduledStakingToken(scheduleId) == 0) &&
        (getScheduledStakingToken(scheduleId) == 0 <=> getScheduledDistributionToken(scheduleId) == 0) &&
        (getScheduledDistributionToken(scheduleId) == 0 <=> getScheduledStartTime(scheduleId) == 0) &&
        (getScheduledStartTime(scheduleId) == 0 <=> getScheduledOwner(scheduleId) == 0) &&
        (getScheduledOwner(scheduleId) == 0 <=> getScheduledAmount(scheduleId) == 0) &&
        (getScheduledAmount(scheduleId) == 0 <=> getScheduledStatus(scheduleId) == 0)

