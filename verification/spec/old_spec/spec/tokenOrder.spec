methods {
    Harness_getPoolTokenByIndex(bytes32, uint256) returns address envfree
    Harness_verifyTwoTokenPoolsTokens(bytes32) returns bool envfree
    Harness_poolIsTwoTokens(bytes32) returns bool envfree
    0xd5c096c4 => NONDET  // onJoinPool
    0x74f3b009 => NONDET // onExitPool
    0x8d928af8 => NONDET // getVault
    0x38fff2d0 => NONDET // getPoolId
    0xb58c9534 => NONDET // onSwapGivenIn for General Pool
    0x618e086e => NONDET // onSwapGivenOut on General Pool
}

rule token_order_is_constant {
    bytes32 poolId;
    require !Harness_poolIsTwoTokens(poolId);

    uint256 index;
    address token_pre = Harness_getPoolTokenByIndex(poolId, index);

    method f;
    require f.selector != deregisterTokens(bytes32,address[]).selector; // changes token order
    require f.selector != 0x45eb8830; //batchSwapGivenOut, times out
    require f.selector != 0x77c6b2c9; //batchSwapGivenIn, times out
    env e;
    calldataarg a;
    f(e, a);

    address token_post = Harness_getPoolTokenByIndex(poolId, index);
    assert token_pre == token_post, 
        "The order of tokens in a pool should never changes besides calls to `registerTokens` and `deregisterTokens`";
}

rule tokens_are_static_two_token_pools {
    bytes32 poolId;
    require Harness_poolIsTwoTokens(poolId);

    uint256 index;
    address token_pre = Harness_getPoolTokenByIndex(poolId, index);

    method f;
    require f.selector != deregisterTokens(bytes32,address[]).selector;
    require f.selector != 0x45eb8830; //batchSwapGivenOut, times out
    require f.selector != 0x77c6b2c9; //batchSwapGivenIn, times out
    env e;
    calldataarg a;
    f(e, a);

    address token_post = Harness_getPoolTokenByIndex(poolId, index);
    assert token_pre == token_post, 
        "The order of tokens in a pool should never changes besides calls to `registerTokens` and `deregisterTokens`";
}

rule valid_order_of_two_pool_tokens {
    bytes32 poolId;
    bool precondition = Harness_verifyTwoTokenPoolsTokens(poolId);
    require precondition;

    method f;
    require f.selector != 0x45eb8830; //batchSwapGivenOut, times out
    require f.selector != 0x77c6b2c9; //batchSwapGivenIn, times out

    env e;
    calldataarg a;
    f(e, a);

    bool postcondition = Harness_verifyTwoTokenPoolsTokens(poolId);
    assert postcondition, "two pool tokens token invariant is broken";
}