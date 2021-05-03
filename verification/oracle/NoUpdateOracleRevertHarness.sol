pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "./WeightedPool2TokensHarness.sol";

contract NoUpdateOracleRevertHarness is WeightedPool2TokensHarness {
    constructor(NewPoolParams memory params) WeightedPool2TokensHarness(params) {} 

    bool public bad_oracle_param = false;

    /**
     * @dev Updates the Price Oracle based on the Pool's current state (balances, BPT supply and invariant). Must be
     * called on *all* state-changing functions with the balances *before* the state change happens, and with
     * `lastChangeBlock` as the number of the block in which any of the balances last changed.
     */
    function _updateOracle(
        uint256 lastChangeBlock,
        uint256 balanceToken0,
        uint256 balanceToken1
    ) internal override {
        if (balanceToken0 == 0 || balanceToken1 == 0) {
            bad_oracle_param = true;
        }
        super._updateOracle(lastChangeBlock, balanceToken0, balanceToken1);
    }
}