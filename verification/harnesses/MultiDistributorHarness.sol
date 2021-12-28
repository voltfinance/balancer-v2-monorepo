pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "../munged/distributors/contracts/MultiDistributor.sol";

contract MultiDistributorHarness is MultiDistributor {
    using Math for uint256;
    using SafeERC20 for IERC20;
    using EnumerableSet for EnumerableSet.Bytes32Set;

    constructor(IVault vault) MultiDistributor(vault) {
        // solhint-disable-previous-line no-empty-blocks
        // MultiDistributor is a singleton, so it simply uses its own address to disambiguate action identifiers
    }

    function getStakingToken(bytes32 distributionId) public view returns (IERC20){
        return _distributions[distributionId].stakingToken;
    }

    function getDistributionToken(bytes32 distributionId) public view returns (IERC20){
        return _distributions[distributionId].distributionToken;
    }

    function getOwner(bytes32 distributionId) public view returns (address){
        return _distributions[distributionId].owner;
    }

    function getTotalSupply(bytes32 distributionId) public view returns (uint256){
        return _distributions[distributionId].totalSupply;
    }

    function getDuration(bytes32 distributionId) public view returns (uint256){
        return _distributions[distributionId].duration;
    }

    function getPeriodFinish(bytes32 distributionId) public view returns (uint256){
        return _distributions[distributionId].periodFinish;
    }

    function getPaymentRate(bytes32 distributionId) public view returns (uint256){
        return _distributions[distributionId].paymentRate;
    }

    function getLastUpdateTime(bytes32 distributionId) public view returns (uint256){
        return _distributions[distributionId].lastUpdateTime;
    }

    function getGlobalTokensPerStake(bytes32 distributionId) public view returns (uint256){
        return _distributions[distributionId].globalTokensPerStake;
    }

    function getUserTokensPerStake(bytes32 distributionId, IERC20 stakingToken, address sender) public view returns (uint256){
        return _userStakings[stakingToken][sender].distributions[distributionId].userTokensPerStake;
    }

    function getUserBalance(IERC20 stakingToken, address sender) public view returns (uint256){
        return _userStakings[stakingToken][sender].balance;
    }

    function getUserSubscribedDistributionIdByIndex(IERC20 stakingToken, address sender, uint256 index) public view returns (bytes32){
        return _userStakings[stakingToken][sender].subscribedDistributions.at(index);
    }

    function getUserSubscribedDistributionIndexById(IERC20 stakingToken, address sender, bytes32 distId) public view returns (uint256 index){
        index = _userStakings[stakingToken][sender].subscribedDistributions.rawIndexOf(distId);
        return index;
    }

    function getUserSetLength(IERC20 stakingToken, address sender) public view returns (uint256){
        return _userStakings[stakingToken][sender].subscribedDistributions.length();
    }

    function getDistIdContainedInUserSubscribedDistribution(IERC20 stakingToken, address sender, bytes32 distId) public view returns (bool isContained){
        isContained = _userStakings[stakingToken][sender].subscribedDistributions.contains(distId);
        return isContained;
    }

    function getUserSubscribedSetArry(IERC20 stakingToken, address user) public view returns (bytes32[] memory){
        return _userStakings[stakingToken][user].subscribedDistributions._values;
    }

    function getUserUnclaimedTokensOfDistribution(bytes32 distributionId, IERC20 stakingToken, address user) public view returns (uint256){
        return _userStakings[stakingToken][user].distributions[distributionId].unclaimedTokens;
    }

    function _lastTimePaymentApplicableHarness(bytes32 distributionId) external view returns (uint256) {
        return _lastTimePaymentApplicable(_getDistribution(distributionId));
    }
}
