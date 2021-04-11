pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "./simplifiedVaultHarness.sol";

contract solvencyHarness is simplifiedVaultHarness {
    /*
    This harness is used for solvency proofs.
    */
    using BalanceAllocation for bytes32;

    constructor(IAuthorizer authorizer) simplifiedVaultHarness(authorizer) {}

    function Harness_isVaultRelayer(address user) public view returns (bool) {
        return _hasAllowedRelayer(address(this), user);
    }

    function Harness_get_collected_fee_of_token (IERC20 token) public view returns (uint256 fee){
        fee = _collectedProtocolFees[token];
    }

    function queryBatchSwap(
        SwapKind kind,
        SwapRequest[] memory swaps,
        IERC20[] memory tokens,
        FundManagement memory funds
    ) external override returns (int256[] memory) {}  // It behaves like a view function

    IERC20[] withdraw_tokens;
    uint256[] withdraw_amounts;

    function Harness_withdrawFromInternalBalance(
        address sender,
        address recipient
    ) public {
        withdrawFromInternalBalance(sender, withdraw_tokens, withdraw_amounts, recipient);
    }

    function Harness_get_pool_cash_like_exit_pool (bytes32 poolId, IERC20 token) public view returns (uint256){
        /*
        In exitPool() and joinPool() we assume the input array of tokens is the same as the array of tokens returned by getPoolTokens.
        As we do not want to check that the arrays are equal (time outs), we use this function instead and drop the assumption.
        */
        IERC20[] memory tokens_array = new IERC20[](1);
        tokens_array[0] = token;
        bytes32[] memory balances = _validateTokensAndGetBalances(poolId, tokens_array);
        return uint256(balances[0]);
    }

    bytes data;

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

}
