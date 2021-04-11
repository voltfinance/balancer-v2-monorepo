pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "./simplifiedVaultHarness.sol";

contract internalBalanceHarness is simplifiedVaultHarness {
    /*
    This harness exposes information used by rules caring about the internal balance.
    */

    constructor(IAuthorizer authorizer) simplifiedVaultHarness(authorizer) {}

    function Harness_isAuthenticatedByUser(address user) public view returns (bool) {
        if (user == msg.sender) return true;
        bool user_approved = _hasAllowedRelayer(user, msg.sender);
        bool sys_approved = authorizations[msg.sender];
        return user_approved && sys_approved;
    }

    address random;

    function Harness_isVaultRelayer() public view returns (bool) {
        return _hasAllowedRelayer(address(this), random);
    }
}