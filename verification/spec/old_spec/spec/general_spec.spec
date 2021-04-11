methods {
    hasAllowedRelayer(address, address) returns bool envfree
    Harness_getGeneralPoolTotalBalance(bytes32, address) returns uint256 envfree
    Harness_minimalSwapInfoPoolIsNotZero(bytes32, address) returns bool envfree
    Harness_twoTokenPoolIsNotZero(bytes32, address) returns bool envfree
    Harness_isPoolRegistered(bytes32) returns bool envfree
}

rule increasingFees {
    calldataarg tokens;
    env e;
    uint256 free_pre = Harness_getACollectedFee(e, tokens); // Gets the collected fees for one type of token

    method f;
    require f.selector != withdrawCollectedFees(address[],uint256[],address).selector;
    calldataarg a;
    f(e, a);

    uint256 free_post = Harness_getACollectedFee(e, tokens); // Get the collected fees for the same token type

    assert free_post >= free_pre, "The collected fees cannot decrease unless they are withdrawn";
} 

rule changeRelayerAllowanceIntegrity {
    address relayer;
    bool allowed;

    env e;
    changeRelayerAllowance(e, relayer, allowed);

    bool allowance = hasAllowedRelayer(e.msg.sender, relayer);
    assert allowance == allowed, "allowance was set right before this check";
}

rule general_pool_positive_total_if_registered {
    bytes32 poolId;
    address token;
    uint256 init_tot_balance = Harness_getGeneralPoolTotalBalance(poolId, token);
    bool init_registered = Harness_isPoolRegistered(poolId);
    require init_tot_balance > 0 => init_registered;

    method f;
    env e;
    calldataarg a;
    f(e, a);

    uint256 fin_tot_balance = Harness_getGeneralPoolTotalBalance(poolId, token);
    bool fin_registered = Harness_isPoolRegistered(poolId);
    assert fin_tot_balance > 0 => fin_registered;
}

rule minimal_swap_info_pool_positive_total_if_registered {
    bytes32 poolId;
    address token;
    bool init_positive_balance = Harness_minimalSwapInfoPoolIsNotZero(poolId, token);
    bool init_registered = Harness_isPoolRegistered(poolId);
    require init_positive_balance => init_registered;

    method f;
    env e;
    calldataarg a;
    f(e, a);

    bool fin_positive_balance = Harness_minimalSwapInfoPoolIsNotZero(poolId, token);
    bool fin_registered = Harness_isPoolRegistered(poolId);
    assert fin_positive_balance => fin_registered, "The total balance of a minimal swap info pool should be positive only if it is registered";
}

// Currently produces an erroneous counter-example
/*
rule two_tokens_pool_positive_total_if_registered {
    bytes32 poolId;
    address token;
    bool init_pos_balance = Harness_twoTokenPoolIsNotZero(poolId, token);
    bool init_registered = Harness_isPoolRegistered(poolId);
    require init_pos_balance => init_registered;

    method f;
    env e;
    calldataarg a;
    f(e, a);

    bool fin_pos_balance = Harness_twoTokenPoolIsNotZero(poolId, token);
    bool fin_registered = Harness_isPoolRegistered(poolId);
    assert fin_pos_balance => fin_registered, "The total balance of a two tokens pool should be positive only if it is registered";
}
*/
