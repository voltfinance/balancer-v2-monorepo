pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "../../contracts/vault/ProtocolFeesCollector.sol";
import "../../contracts/vault/interfaces/IVault.sol";

contract FeeHarness is ProtocolFeesCollector {
    constructor(IVault vault) ProtocolFeesCollector(vault) {}

    function Harness_get_max_swap_fee() public pure returns (uint256) {
        return _MAX_PROTOCOL_SWAP_FEE_PERCENTAGE; // 50%
    }

    function Harness_get_max_flash_loan_fee() external pure returns (uint256) {
        return _MAX_PROTOCOL_FLASH_LOAN_FEE_PERCENTAGE; // 50%
    }

    function Harness_one() external pure returns (uint256) {
        return 1e18;
    }
}
