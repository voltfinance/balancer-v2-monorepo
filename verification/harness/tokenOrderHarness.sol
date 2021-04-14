pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "./simplifiedVaultHarness.sol";

contract tokenOrderHarness is simplifiedVaultHarness {
    /*
    This harness exposes information used by rules caring about token order of the pools.
    */

    constructor(IAuthorizer authorizer,
        IWETH weth,
        uint256 emergencyPeriod,
        uint256 emergencyPeriodCheckExtension
    ) simplifiedVaultHarness (authorizer, weth, emergencyPeriod, emergencyPeriodCheckExtension) { }

    function Harness_getPoolTokenByIndex(bytes32 poolId, uint256 index) public view returns (IERC20 token) {
        IERC20[] memory token_array; 
        bytes32[] memory dummy;
        (token_array, dummy) = _getPoolTokens(poolId);
        return token_array[index];
    }

    // function Harness_deregister_a_single_token(bytes32 poolId, IERC20 token) public {
    //     IERC20[] memory token_array = new IERC20[](1);
    //     token_array[0] = token;
    //     deregisterTokens(poolId, token_array);
    // }

    function Harness_verifyTwoTokenPoolsTokens(bytes32 poolId) public view returns (bool) {
        PoolSpecialization specialization = _getPoolSpecialization(poolId);
        require (specialization == PoolSpecialization.TWO_TOKEN);
        IERC20[] memory tokens; 
        bytes32[] memory balances;
        (tokens, balances) = _getTwoTokenPoolTokens(poolId);
        
        if (tokens.length == 0) return true;
        IERC20 tokenA = tokens[0];
        IERC20 tokenB = tokens[1];
        if (tokenA < tokenB) return true;
        return false;
    }
}