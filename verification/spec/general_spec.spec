using DummyERC20 as ERC20
using WETH as weth
using Borrower as borrower
using ProtocolFeesCollector as feesCollector

methods {
    hasApprovedRelayer(address, address) returns bool envfree
    Harness_GeneralPoolTotalBalanceIsNotZero(bytes32, address) returns bool envfree
    Harness_minimalSwapInfoPoolIsNotZero(bytes32, address) returns bool envfree
    Harness_isPoolRegistered(bytes32) returns bool envfree
    Harness_has_valid_signature(address) returns bool envfree
    Harness_poolIsMinimal(bytes32) returns bool envfree
    Harness_poolIsGeneral(bytes32) returns bool envfree
    Harness_isTokenRegisteredForMinimalSwapPool(bytes32,address) returns bool envfree

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

function legalAddress(address suspect) {
    require suspect != currentContract;
    require suspect != ERC20;
    require suspect != weth;
    require suspect != borrower;
    require suspect != feesCollector;
}

function legalPool(bytes32 pool) {
    require pool != currentContract;
    require pool != ERC20;
    require pool != weth;
    require pool != borrower;
    require pool != feesCollector;
}

function noIllegalRelayer(address suspect) {
    require !hasApprovedRelayer(currentContract, suspect);
    require !hasApprovedRelayer(ERC20, suspect);
    require !hasApprovedRelayer(weth, suspect);
    require !hasApprovedRelayer(borrower, suspect);
    require !hasApprovedRelayer(feesCollector, suspect);

    require !Harness_has_valid_signature(currentContract);
    require !Harness_has_valid_signature(ERC20);
    require !Harness_has_valid_signature(weth);
    require !Harness_has_valid_signature(borrower);
    require !Harness_has_valid_signature(feesCollector);
}

rule increasingFees {
    calldataarg tokens;
    env e;
    uint256 free_pre = Harness_getACollectedFee(e, tokens); // Gets the collected fees for one type of token

    method f;
    require f.selector != 0x945bcec9; // batchswap
    calldataarg a;
    legalAddress(e.msg.sender);
    noIllegalRelayer(e.msg.sender);
    f(e, a);

    uint256 free_post = Harness_getACollectedFee(e, tokens); // Get the collected fees for the same token type

    assert free_post >= free_pre, "The collected fees cannot decrease by any vault action";
} 

rule setRelayerApprovalIntegrity {
    address relayer;
    bool allowed;

    env e;
    setRelayerApproval(e, e.msg.sender, relayer, allowed);

    bool allowance = hasApprovedRelayer(e.msg.sender, relayer);
    assert allowance == allowed, "allowance was set right before this check";
}

rule general_pool_positive_total_if_registered {
    bytes32 poolId;
    require Harness_poolIsGeneral(poolId);
    legalPool(poolId);

    address token;
    bool init_tot_balance_positive = Harness_GeneralPoolTotalBalanceIsNotZero(poolId, token);
    bool init_registered = Harness_isPoolRegistered(poolId);
    require init_tot_balance_positive => init_registered;

    method f;
    require f.selector != 0x945bcec9; // batchswap
    env e;
    legalAddress(e.msg.sender);
    noIllegalRelayer(e.msg.sender);
    calldataarg a;
    f(e, a);

    bool fin_tot_balance_positive = Harness_GeneralPoolTotalBalanceIsNotZero(poolId, token);
    bool fin_registered = Harness_isPoolRegistered(poolId);
    assert fin_tot_balance_positive => fin_registered;
}

rule minimal_swap_info_pool_positive_total_if_registered {
    method f;
    require f.selector != 0x945bcec9; // batchswap

    bytes32 poolId;
    require Harness_poolIsMinimal(poolId);
    legalPool(poolId);

    address token;
    bool init_positive_balance = Harness_minimalSwapInfoPoolIsNotZero(poolId, token);
    bool init_registered = Harness_isPoolRegistered(poolId);
    require init_positive_balance => init_registered;
    requireInvariant tokensPoolRegistration(poolId, token);

    env e;
    legalAddress(e.msg.sender);
    noIllegalRelayer(e.msg.sender);
    calldataarg a;
    f(e, a);

    bool fin_positive_balance = Harness_minimalSwapInfoPoolIsNotZero(poolId, token);
    bool fin_registered = Harness_isPoolRegistered(poolId);
    assert fin_positive_balance => fin_registered, "The total balance of a minimal swap info pool should be positive only if it is registered";
}

// If tokens are registered, then pool must be registered as well
invariant tokensPoolRegistration(bytes32 poolId, address token) 
    Harness_isTokenRegisteredForMinimalSwapPool(poolId, token) => Harness_isPoolRegistered(poolId)