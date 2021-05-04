using NoUpdateOracleRevertHarness as oracle_pool
using DummyERC20 as ERC20A
using DummyERC20B as ERC20B
using WETH as weth
using Borrower as borrower
using ProtocolFeesCollector as feesCollector

methods {
    hasApprovedRelayer(address, address) returns bool envfree
    Harness_has_valid_signature(address) returns bool envfree

    Harness_twoTokensPoolIsNotZero(bytes32, address) returns bool envfree
    getPoolId() returns bytes32 envfree => DISPATCHER(true)

    bad_oracle_param() envfree => DISPATCHER(true)

    // token functions
    transfer(address, uint256) returns bool envfree => DISPATCHER(true)
    transferFrom(address, address, uint256) returns bool envfree => DISPATCHER(true)
    balanceOf(address) returns uint256 envfree => DISPATCHER(true)
    totalSupply() returns uint256 envfree => DISPATCHER(true)
    

    0xd5c096c4 => DISPATCHER(true) // onJoinPool
    0x74f3b009 => DISPATCHER(true) // onExitPool

    // Others
    // receiveFlashLoan(address[], uint256[], uint256[], bytes) => NONDET

    nop() => NONDET
}

function legalAddress(address suspect) {
    require suspect != currentContract;
    require suspect != ERC20A;
    require suspect != ERC20B;
    require suspect != weth;
    require suspect != feesCollector;
    require suspect != oracle_pool;
}

function noIllegalRelayer(address suspect) {
    require !hasApprovedRelayer(currentContract, suspect);
    require !hasApprovedRelayer(ERC20A, suspect);
    require !hasApprovedRelayer(ERC20B, suspect);
    require !hasApprovedRelayer(weth, suspect);
    require !hasApprovedRelayer(feesCollector, suspect);
    require !hasApprovedRelayer(oracle_pool, suspect);

    require !Harness_has_valid_signature(currentContract);
    require !Harness_has_valid_signature(ERC20A);
    require !Harness_has_valid_signature(ERC20B);
    require !Harness_has_valid_signature(weth);
    require !Harness_has_valid_signature(feesCollector);
    require !Harness_has_valid_signature(oracle_pool);
}

rule oracle_balance_positive_after_join {
    bytes32 poolId = oracle_pool.getPoolId();
    env e;
    address sender;
    legalAddress(sender);
    noIllegalRelayer(sender);
    address recipient;

    uint256 maxAmountInA;
    uint256 maxAmountInB;
    bool fromInternalBalance;

    Harness_doubleJoinPool(e, poolId, sender, recipient, ERC20A, ERC20B, maxAmountInA, maxAmountInB, fromInternalBalance);

    assert Harness_twoTokensPoolIsNotZero(poolId, ERC20A);
}

rule oracle_balance_positive_after_positive {
    bytes32 poolId = oracle_pool.getPoolId();
    require Harness_twoTokensPoolIsNotZero(poolId, ERC20A);

    env e;
    calldataarg a;
    method f;
    f(e, a);

    assert Harness_twoTokensPoolIsNotZero(poolId, ERC20A);
}

rule no_bad_oracle_param {
    require !oracle_pool.bad_oracle_param();

    bytes32 poolId = oracle_pool.getPoolId();
    require Harness_twoTokensPoolIsNotZero(poolId, ERC20A);

    env e;
    calldataarg a;
    method f;
    f(e, a);

    assert !oracle_pool.bad_oracle_param();
}
