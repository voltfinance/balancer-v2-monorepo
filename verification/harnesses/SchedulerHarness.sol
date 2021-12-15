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

    function getScheduledStakingToken(bytes32 distributionId) public view returns (IERC20){
        return _scheduledDistributions[distributionId].stakingToken;
    }

    function getScheduledDistributionToken(bytes32 distributionId) public view returns (IERC20){
        return _scheduledDistributions[distributionId].distributionToken;
    }

    function getScheduledStartTime(bytes32 distributionId) public view returns (uint256){
        return _scheduledDistributions[distributionId].startTime;
    }

    function getScheduledOwner(bytes32 distributionId) public view returns (address){
        return _scheduledDistributions[distributionId].owner;
    }

    function getScheduledAmount(bytes32 distributionId) public view returns (uint256){
        return _scheduledDistributions[distributionId].amount;
    }

    function getScheduledStatus(bytes32 distributionId) public view returns (DistributionStatus){
        return _scheduledDistributions[distributionId].status;
    }
}

