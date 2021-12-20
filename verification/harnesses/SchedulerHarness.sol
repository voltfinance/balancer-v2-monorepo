pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "../munged/distributors/contracts/DistributionScheduler.sol";

contract SchedulerHarness is DistributionScheduler {
    using SafeERC20 for IERC20;

    constructor(IMultiDistributor multiDistributor) DistributionScheduler(multiDistributor) {
    }

    function getScheduledDistributionId(bytes32 scheduleId) public view returns (bytes32){
        return _scheduledDistributions[scheduleId].distributionId;
    }

    function getScheduledStartTime(bytes32 scheduleId) public view returns (uint256){
        return _scheduledDistributions[scheduleId].startTime;
    }

    function getScheduledAmount(bytes32 scheduleId) public view returns (uint256){
        return _scheduledDistributions[scheduleId].amount;
    }

    function getScheduledStatus(bytes32 scheduleId) public view returns (DistributionStatus){
        return _scheduledDistributions[scheduleId].status;
    }
}

