using DummyERC20 as ERC20
using WETH as weth
using Borrower as borrower
using ProtocolFeesCollector as feesCollector

methods {
    Harness_getPoolTokenByIndex(bytes32, uint256) returns address envfree
    Harness_verifyTwoTokenPoolsTokens(bytes32) returns bool envfree
    Harness_poolIsTwoTokens(bytes32) returns bool envfree

    // token functions
    transfer(address, uint256) returns bool envfree => DISPATCHER(true)
    transferFrom(address, address, uint256) returns bool envfree => DISPATCHER(true)
    balanceOf(address) returns uint256 envfree => DISPATCHER(true)
    totalSupply() returns uint256 envfree => DISPATCHER(true)

    // Pool hooks
    // onSwap(address,uint256[],uint256,uint256) returns uint256 => NONDET // general pool
    0x01ec954a => NONDET // onSwap hook of a general pool
    // onSwap(address,uint256,uint256) returns uint256 => NONDET // minimal swap info pool
    0x9d2c110c => NONDET // onSwap hook of a minimal swap info pool

    0xd5c096c4 => NONDET // onJoinPool
    0x74f3b009 => NONDET // onExitPool

    // Others
    receiveFlashLoan(address[], uint256[], uint256[], bytes) => DISPATCHER(true)

    nop() => NONDET
}

function legalPool(bytes32 pool) {
    require pool != currentContract;
    require pool != ERC20;
    require pool != weth;
    require pool != borrower;
    require pool != feesCollector;
}

rule token_order_is_constant {
    bytes32 poolId;
    require !Harness_poolIsTwoTokens(poolId);
    legalPool(poolId);

    uint256 index;
    address token_pre = Harness_getPoolTokenByIndex(poolId, index);

    method f;
    require f.selector != deregisterTokens(bytes32,address[]).selector; // changes token order
    require f.selector != 0x945bcec9; // batchswap
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
    require f.selector != 0x945bcec9; // batchswap
    env e;
    calldataarg a;
    f(e, a);

    address token_post = Harness_getPoolTokenByIndex(poolId, index);
    assert token_pre == token_post, 
        "The order of tokens in a pool should never changes besides calls to `registerTokens` and `deregisterTokens`";
}

rule valid_order_of_two_pool_tokens {
    bytes32 poolId;
    legalPool(poolId);
    bool precondition = Harness_verifyTwoTokenPoolsTokens(poolId);
    require precondition;

    method f;
    require f.selector != 0x945bcec9; // batchswap

    env e;
    calldataarg a;
    f(e, a);

    bool postcondition = Harness_verifyTwoTokenPoolsTokens(poolId);
    assert postcondition, "two pool tokens token invariant is broken";
}