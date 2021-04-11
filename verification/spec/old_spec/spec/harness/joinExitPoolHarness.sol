pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

// import "../../contracts/vault/Authorization.sol";
import "../../contracts/vault/PoolRegistry.sol";
import "./simplifiedVaultHarness.sol";

contract JoinExitPoolHarness is simplifiedVaultHarness {
    constructor(IAuthorizer authorizer) simplifiedVaultHarness(authorizer) {}

    /*
    function joinPool(
        bytes32 poolId,
        address sender,
        address recipient,
        IERC20[] memory tokens,
        uint256[] memory maxAmountsIn,
        bool fromInternalBalance,
        bytes memory userData
    ) external override nonReentrant withRegisteredPool(poolId) authenticateFor(sender) {
    */

    bytes data;

    function Harness_singleJoinPool(bytes32 poolId, address sender, address recipient, IERC20 token, uint256 maxAmountIn, bool fromInternalBalance) public {
        IERC20[] memory tokens_array = new IERC20[](1);
        tokens_array[0] = token;
        uint256[] memory amounts_array = new uint256[](1);
        amounts_array[0] = maxAmountIn;
        joinPool(poolId, sender, recipient, tokens_array, amounts_array, fromInternalBalance, data);
    }

    function Harness_doubleJoinPool(bytes32 poolId, address sender, address recipient, IERC20 token_a, IERC20 token_b, 
                                     uint256 maxAmountInA, uint256 maxAmountInB, bool fromInternalBalance) public {

        IERC20[] memory tokens_array = new IERC20[](2);
        tokens_array[0] = token_a;
        tokens_array[1] = token_b;

        uint256[] memory amounts_array = new uint256[](2);
        amounts_array[0] = maxAmountInA;
        amounts_array[1] = maxAmountInB;

        joinPool(poolId, sender, recipient, tokens_array, amounts_array, fromInternalBalance, data);
    }

    function getTokenBalance(address user, IERC20 token) public view returns (uint256) {
        return token.balanceOf(user);
    }

    /*
        function exitPool(
        bytes32 poolId,
        address sender,
        address recipient,
        IERC20[] memory tokens,
        uint256[] memory minAmountsOut,
        bool toInternalBalance,
        bytes memory userData
    )
    */

    function Harness_singleExitPool(bytes32 poolId, address sender, address recipient, IERC20 token,
                                    uint256 minAmountOut, bool toInternalBalance) public {
        IERC20[] memory tokens_array = new IERC20[](1);
        tokens_array[0] = token;
        uint256[] memory amounts_array = new uint256[](1);
        amounts_array[0] = minAmountOut;
        exitPool(poolId, sender, recipient, tokens_array, amounts_array, toInternalBalance, data);
    }

    function Harness_doubleExitPool(bytes32 poolId, address sender, address recipient, IERC20 token_a, 
                                    IERC20 token_b, uint256 minAmountOutA, uint256 minAmountOutB, 
                                    bool toInternalBalance) public {
        IERC20[] memory tokens_array = new IERC20[](2);
        tokens_array[0] = token_a;
        tokens_array[1] = token_b;

        uint256[] memory amounts_array = new uint256[](2);
        amounts_array[0] = minAmountOutA;
        amounts_array[1] = minAmountOutB;

        exitPool(poolId, sender, recipient, tokens_array, amounts_array, toInternalBalance, data);
    }

    function Harness_get_pool_cash_like_exit_pool (bytes32 poolId, IERC20 token) public view returns (uint256){
        IERC20[] memory tokens_array = new IERC20[](1);
        tokens_array[0] = token;
        bytes32[] memory balances = _validateTokensAndGetBalances(poolId, tokens_array);
        return uint256(balances[0]);
    }

    function Harness_get_withdraw_fee() public view returns (uint256) {
        return _protocolWithdrawFee;
    }

}