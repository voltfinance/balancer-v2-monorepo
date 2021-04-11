pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "./simplifiedVaultHarness.sol";

contract simplifiedatchHarness is simplifiedVaultHarness {
    constructor(IAuthorizer authorizer) simplifiedVaultHarness(authorizer) {}


    /**
     * Simplifications:
        * No reentrancy check
        * no deadline check
        * no ensureInputLengthMatch
        * no checks of swap limits
        * unsafe casts fron uint256 to int256
        * safetransfer to Transfer
     */
    function _batchSwap(
        SwapRequest[] memory swaps,
        IERC20[] memory tokens,
        FundManagement memory funds,
        int256[] memory limits,
        uint256 deadline,
        SwapKind kind
    // ) private nonReentrant returns (int256[] memory tokenDeltas) {
    ) private returns (int256[] memory tokenDeltas) {
        // The deadline is timestamp-based: it should not be relied on having sub-minute accuracy.
        // solhint-disable-next-line not-rely-on-time
        // require(block.timestamp <= deadline, "SWAP_DEADLINE"); // Commented for simplicity

        // InputHelpers.ensureInputLengthMatch(tokens.length, limits.length);

        // Perform the swaps, updating the Pool token balances and computing the net Vault token deltas.
        tokenDeltas = _swapWithPools(swaps, tokens, funds, kind);

        // Process token deltas, by either transferring tokens from the sender (for positive deltas) or to the recipient
        // (for negative deltas).
        for (uint256 i = 0; i < tokens.length; ++i) {
            IERC20 token = tokens[i];
            int256 delta = tokenDeltas[i];

            // require(delta <= limits[i], "SWAP_LIMIT");

            // Ignore zeroed deltas
            if (delta > 0) {
                _receiveTokens(token, uint256(delta), funds.sender, funds.fromInternalBalance);
            } else if (delta < 0) {
                uint256 toSend = uint256(-delta);

                if (funds.toInternalBalance) {
                    _increaseInternalBalance(funds.recipient, token, toSend);
                } else {
                    // Note protocol withdraw fees are not charged in this transfer
                    // token.safeTransfer(funds.recipient, toSend);
                    token.transfer(funds.recipient, toSend);
                }
            }
        }
    }
}