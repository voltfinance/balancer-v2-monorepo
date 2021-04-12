using DummyERC20 as ERC20
using WETH as weth
using Borrower as borrower
using ProtocolFeesCollector as feesCollector

methods {
    hasAllowedRelayer(address, address) returns bool envfree
    Harness_getGeneralPoolTotalBalance(bytes32, address) returns uint256 envfree
    Harness_minimalSwapInfoPoolIsNotZero(bytes32, address) returns bool envfree
    Harness_isPoolRegistered(bytes32) returns bool envfree

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
    receiveFlashLoan(address[], uint256[], uint256[], bytes) => DISPATCHER(true) // maybe NONDET?
}

function legalAddress(address suspect) {
    require suspect != currentContract;
    require suspect != ERC20;
    require suspect != weth;
    require suspect != borrower;
    require suspect != feesCollector;
}

rule increasingFees {
    calldataarg tokens;
    env e;
    uint256 free_pre = Harness_getACollectedFee(e, tokens); // Gets the collected fees for one type of token

    method f;
    calldataarg a;
    legalAddress(e.msg.sender);
    f(e, a);

    uint256 free_post = Harness_getACollectedFee(e, tokens); // Get the collected fees for the same token type

    assert free_post >= free_pre, "The collected fees cannot decrease by any vault action";
} 

rule changeRelayerAllowanceIntegrity {
    address relayer;
    bool allowed;

    env e;
    changeRelayerAllowance(e, e.msg.sender, relayer, allowed);

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
    legalAddress(e.msg.sender);
    calldataarg a;
    f(e, a);

    uint256 fin_tot_balance = Harness_getGeneralPoolTotalBalance(poolId, token);
    bool fin_registered = Harness_isPoolRegistered(poolId);
    assert fin_tot_balance > 0 => fin_registered;
}

rule minimal_swap_info_pool_positive_total_if_registered {
    method f;
    bytes32 poolId;
    address token;
    bool init_positive_balance = Harness_minimalSwapInfoPoolIsNotZero(poolId, token);
    bool init_registered = Harness_isPoolRegistered(poolId);
    require init_positive_balance => init_registered;

    env e;
    legalAddress(e.msg.sender);
    calldataarg a;
    f(e, a);

    bool fin_positive_balance = Harness_minimalSwapInfoPoolIsNotZero(poolId, token);
    bool fin_registered = Harness_isPoolRegistered(poolId);
    assert fin_positive_balance => fin_registered, "The total balance of a minimal swap info pool should be positive only if it is registered";
}
