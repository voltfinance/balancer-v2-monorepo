pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "../contracts/vault/Fees.sol";
import "../contracts/vault/Vault.sol";
import "../contracts/vault/interfaces/IAuthorizer.sol";
import "../contracts/vault/Authorization.sol";

contract FeeHarness is Vault {
    constructor(IAuthorizer authorizer) Vault(authorizer) {}

    function Harness_get_swap_fee() public view returns (uint256) {
        return _getProtocolSwapFee();
    }

    function Harness_get_max_swap_fee() public pure returns (uint256) {
        return _MAX_PROTOCOL_SWAP_FEE; // 50%
    }

    function Harness_get_withdraw_fee() public view returns (uint256) {
        return _protocolWithdrawFee;
    }

    function Harness_get_max_withdraw_fee() external pure returns (uint256) {
        return _MAX_PROTOCOL_WITHDRAW_FEE; // 2%
    }

    function Harness_get_flash_loan_fee() public view returns (uint256) {
        return _protocolFlashLoanFee;
    }

    function Harness_get_max_flash_loan_fee() external pure returns (uint256) {
        return _MAX_PROTOCOL_FLASH_LOAN_FEE; // 50%
    }

    function Harness_one() external pure returns (uint256) {
        return 1e18;
    }

    function init_state() public {}
}
