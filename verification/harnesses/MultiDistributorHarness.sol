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

    // mapping(IERC20 => mapping(address => mapping(bytes32 => bool))) public dummyUserSubscriptions;
    // mapping(IERC20 => mapping(address => uint256)) public dummyUserStakings;


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
        require(index<_userStakings[stakingToken][sender].subscribedDistributions.length());
        return index;
    }

    function getDistIdContainedInUserSubscribedDistribution(IERC20 stakingToken, address sender, bytes32 distId) public view returns (bool isContained){
        isContained = _userStakings[stakingToken][sender].subscribedDistributions.contains(distId);
        return isContained;
    }

    /*
    function subscribeDistributions(bytes32[] calldata distributionIds) public virtual override {
        super.subscribeDistributions(distributionIds);
        
        address user = msg.sender;
        
        bytes32 distributionId;
        Distribution storage distribution;
        for (uint256 i; i < distributionIds.length; i++) {
            distributionId = distributionIds[i];
            distribution = _getDistribution(distributionId);
            IERC20 stakingToken = distribution.stakingToken;
            
            dummyUserSubscriptions[stakingToken][user][distributionId] = true;
        }
    }

    function unsubscribeDistributions(bytes32[] calldata distributionIds) public virtual override {
        super.unsubscribeDistributions(distributionIds);
        
        address user = msg.sender;
        
        bytes32 distributionId;
        Distribution storage distribution;
        for (uint256 i; i < distributionIds.length; i++) {
            distributionId = distributionIds[i];
            distribution = _getDistribution(distributionId);
            IERC20 stakingToken = distribution.stakingToken;
            
            dummyUserSubscriptions[stakingToken][user][distributionId] = false;
        }
    }

    
    function stake(IERC20 stakingToken, uint256 amount, address sender, address recipient) public virtual override {
        super.stake(stakingToken, amount, sender, recipient);
        _stakeHarness(stakingToken, amount, sender, recipient);
    }

    function stakeUsingVault(IERC20 stakingToken, uint256 amount, address sender, address recipient) public virtual override {
        super.stakeUsingVault(stakingToken, amount, sender, recipient);
        _stakeHarness(stakingToken, amount, sender, recipient);
    }

    function stakeWithPermit(IERC20 stakingToken, uint256 amount, address sender, uint256 deadline, uint8 v, bytes32 r, bytes32 s) public virtual override {
        super.stakeWithPermit(stakingToken, amount, sender, deadline, v, r, s);
        _stakeHarness(stakingToken, amount, sender, sender);
    }

    function unstake(IERC20 stakingToken, uint256 amount, address sender, address recipient) public virtual override {
        super.unstake(stakingToken, amount, sender, recipient);
        _unstakeHarness(stakingToken, amount, sender, recipient);
    }
    
    function _stakeHarness(IERC20 stakingToken, uint256 amount, address sender, address recipient) private {
        UserStaking storage userStaking = _userStakings[stakingToken][recipient];
        EnumerableSet.Bytes32Set storage distributions = userStaking.subscribedDistributions;
        uint256 distributionsLength = distributions.length();
        
        bytes32 distributionId;
        Distribution storage distribution;
        for (uint256 i; i < distributionsLength; i++) {
            distributionId = distributions.unchecked_at(i);
            distribution = _getDistribution(distributionId);
            dummyUserStakings[stakingToken][recipient] += amount;
        }
    }

    function _unstakeHarness(IERC20 stakingToken, uint256 amount, address sender, address recipient) private {
        UserStaking storage userStaking = _userStakings[stakingToken][recipient];
        EnumerableSet.Bytes32Set storage distributions = userStaking.subscribedDistributions;
        uint256 distributionsLength = distributions.length();
        
        bytes32 distributionId;
        Distribution storage distribution;
        for (uint256 i; i < distributionsLength; i++) {
            distributionId = distributions.unchecked_at(i);
            distribution = _getDistribution(distributionId);
            dummyUserStakings[stakingToken][recipient] -= amount;
        }
    }

    function exit(IERC20[] memory stakingTokens, bytes32[] calldata distributionIds) public virtual override nonReentrant { // HARNESSES: external -> public and made it virtual
        super.exit(stakingTokens, distributionIds);
        for (uint256 i; i < stakingTokens.length; i++) {
            IERC20 stakingToken = stakingTokens[i];
            UserStaking storage userStaking = _userStakings[stakingToken][msg.sender];
            _unstakeHarness(stakingToken, userStaking.balance, msg.sender, msg.sender);
        }
    }

    function exitWithCallback(
        IERC20[] calldata stakingTokens,
        bytes32[] calldata distributionIds,
        IDistributorCallback callbackContract,
        bytes calldata callbackData
    ) public virtual override nonReentrant { // HARNESSES: external -> public and made it virtual
        super.exitWithCallback(stakingTokens, distributionIds, callbackContract, callbackData);
        for (uint256 i; i < stakingTokens.length; i++) {
            IERC20 stakingToken = stakingTokens[i];
            UserStaking storage userStaking = _userStakings[stakingToken][msg.sender];
            _unstakeHarness(stakingToken, userStaking.balance, msg.sender, msg.sender);
        }
    }
    */

    function getUserSubscribedSetArry(IERC20 stakingToken, address user) public view returns (bytes32[] memory){
        return _userStakings[stakingToken][user].subscribedDistributions._values;
    }

    function getUserUnclaimedTokensOfDistribution(bytes32 distributionId, IERC20 stakingToken, address user) public view returns (uint256){
        return _userStakings[stakingToken][user].distributions[distributionId].unclaimedTokens;
    }

    function _lastTimePaymentApplicable(Distribution storage distribution) internal view override returns (uint256) {
        return super._lastTimePaymentApplicable(distribution);
    }
}
