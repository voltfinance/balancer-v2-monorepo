pragma solidity ^0.7.0;

import "../munged/distributors/contracts/MultiDistributor.sol";

contract MultiDistributorHarness is MultiDistributor {
    constructor(IVault vault) MultiDistributor(vault) {
        // solhint-disable-previous-line no-empty-blocks
        // MultiDistributor is a singleton, so it simply uses its own address to disambiguate action identifiers
    }

    function getGlobalTokensPerStake(bytes32 distributionId) public view returns (uint256){
        return _distributions[distributionIds].globalTokensPerStake;
    }

    function getUserTokensPerStake(bytes32 distributionId, IERC20 stakingToken, address sender) public view returns (uint256){
        return _userStakings[stakingToken][sender].distributions[distributionId].userTokensPerStake;
    }

}