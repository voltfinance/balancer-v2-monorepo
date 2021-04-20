pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "./JoinExitPoolHarness.sol";

contract solvencyHarness is JoinExitPoolHarness {
    /*
    This harness is used for solvency proofs.
    */
    using BalanceAllocation for bytes32;

    constructor(IAuthorizer authorizer,
        IWETH weth,
        uint256 emergencyPeriod,
        uint256 emergencyPeriodCheckExtension
    ) JoinExitPoolHarness(authorizer, weth, emergencyPeriod, emergencyPeriodCheckExtension) { }

    function Harness_isVaultRelayer(address user) public view returns (bool) {
        return _hasApprovedRelayer(address(this), user);
    }

}
