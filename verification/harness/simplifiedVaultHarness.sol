pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "../../contracts/vault/Fees.sol";
import "../../contracts/vault/Vault.sol";
import "../../contracts/vault/interfaces/IAuthorizer.sol";
import "../../contracts/vault/VaultAuthorization.sol";

contract simplifiedVaultHarness is Vault {
    /*
    This harness simplifies mathematical operations of the vault for an easier verification.
    We simplify the following:
    - Authorization by the external Authorizer is simplified to checking boolean values in a map.
    - Fee calculation is simplified to return a fixed smaller integer than the amount we tax.
    - Specialization of a pool is just checking it from a map.
    */
    using BalanceAllocation for bytes32;

    constructor(IAuthorizer authorizer) Vault(authorizer) {}

    /* Bypassing the external Authorizer */


    mapping(address => bool) internal authorizations;

    function _authenticateCaller() override internal view {
        require(authorizations[msg.sender]);
    }

    /* Simplifying fee calculations */


    mapping(uint256 => uint256) private calc_fee; // All fee types will return the same value for simplicity

    function _calculateFlashLoanFee(uint256 amount) override internal view returns (uint256) {
        if (_getProtocolFeesCollector().getFlashLoanFee() == 0) return 0; // havoc as CONSTANT
        uint256 fee = calc_fee[amount];
        require(fee < amount);
        return fee;
    }

    function Harness_calc_fee(uint256 amount) public view returns (uint256) {
        return calc_fee[amount];
    }

    function Harness_getACollectedFee(IERC20 token) public view returns (uint256) {
        IERC20[] memory token_array = new IERC20[](1);
        token_array[0] = token;
        uint256 result = _getProtocolFeesCollector().getCollectedFees(token_array)[0]; // havoc as DISPATCHER
        return result;
    }

    /* Simplifying specialization checks */

    mapping(bytes32 => PoolSpecialization) private specializations;

    function _getPoolSpecialization(bytes32 poolId) override view internal returns (PoolSpecialization) {
        // require (specializations[poolId] == PoolSpecialization.GENERAL || 
        //          specializations[poolId] == PoolSpecialization.MINIMAL_SWAP_INFO || 
        //          specializations[poolId] == PoolSpecialization.TWO_TOKEN);
        return specializations[poolId];
    }

    function Harness_poolIsTwoTokens(bytes32 poolId) public view returns (bool) {
        return specializations[poolId] == PoolSpecialization.TWO_TOKEN;
    }

    function Harness_poolIsGeneral(bytes32 poolId) public view returns (bool) {
        return specializations[poolId] == PoolSpecialization.GENERAL;
    }

    //// exposers

    function Harness_isPoolRegistered(bytes32 poolId) public view returns (bool){
        return _isPoolRegistered[poolId];
    }

    function Harness_getGeneralPoolTotalBalance(bytes32 poolId, IERC20 token) public view returns (uint256) {
        bytes32 currentBalance = _getGeneralPoolBalance(poolId, token);
        // return currentBalance.total();
        return uint256(currentBalance);
    }

    /**
    * @dev Returns true if `balance`'s total balance is zero. Costs less gas than computing the total.
    */
    function Harness_minimalSwapInfoPoolIsNotZero(bytes32 poolId, IERC20 token) public view returns (bool) {
        bytes32 currentBalance = _getMinimalSwapInfoPoolBalance(poolId, token);
        return currentBalance.isNotZero();
    }

    /**
    * @dev Returns true if `balance`'s total balance is zero. Costs less gas than computing the total.
    */
    function Harness_twoTokenPoolIsNotZero(bytes32 poolId, IERC20 token) public view returns (bool) {
        bytes32 currentBalance = _getTwoTokenPoolBalance(poolId, token);
        return currentBalance.isNotZero();
    }

    function init_state() public pure {}

    function Harness_getAnInternalBalance(address user, IERC20 token) public view returns (uint256) {
        IERC20[] memory token_array = new IERC20[](1);
        token_array[0] = token;
        uint256 result = _getInternalBalance(user, token_array)[0];
        return result;
    }
}