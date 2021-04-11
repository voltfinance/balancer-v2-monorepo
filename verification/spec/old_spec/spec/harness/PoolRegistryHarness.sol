pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "../../contracts/vault/Fees.sol";
import "../../contracts/vault/Vault.sol";
import "../../contracts/vault/interfaces/IAuthorizer.sol";
import "../../contracts/vault/Authorization.sol";

contract PoolRegistryHarness is Vault {
    constructor(IAuthorizer authorizer) Vault(authorizer) { }

    function toPoolId(address pool, uint specialization, uint80 nonce) public pure returns (bytes32) {
        PoolSpecialization p;
        if (specialization == 0) {
            p = PoolSpecialization.GENERAL;
        } else if (specialization == 1) {
            p = PoolSpecialization.MINIMAL_SWAP_INFO;
        } else {
            p = PoolSpecialization.TWO_TOKEN;
        }
        return _toPoolId(pool, p, nonce);
    }

    function getPoolAddress(bytes32 poolId) public pure returns (address) {
        return _getPoolAddress(poolId);
    }

}