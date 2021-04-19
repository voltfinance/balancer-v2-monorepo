using DummyERC20 as ERC20
using WETH as weth
using Borrower as borrower
using ProtocolFeesCollector as feesCollector

methods {
    Harness_getACollectedFee(address) returns uint256 envfree
    _getInternalBalance(address, address) returns uint256 envfree
    Harness_poolIsTwoTokens(bytes32) returns bool envfree
    getTokenBalance(address, address) returns uint256 envfree
    Harness_poolIsGeneral(bytes32) returns bool envfree
    hasApprovedRelayer(address, address) returns bool envfree
    Harness_has_valid_signature(address) returns bool envfree

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
    // require suspect != borrower;
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
    // require !hasApprovedRelayer(borrower, suspect);
    require !hasApprovedRelayer(feesCollector, suspect);

    require !Harness_has_valid_signature(currentContract);
    require !Harness_has_valid_signature(ERC20);
    require !Harness_has_valid_signature(weth);
    // require !Harness_has_valid_signature(borrower);
    require !Harness_has_valid_signature(feesCollector);
}

/* The rule below is a weaker form of rules to follow. It it useful for debugging if the more complex rules fail.
*/
rule joinPoolProfitability {
    env e;
    address token_checked;

    bytes32 poolId;
    address sender;
    address recipient;

    address token_a;
    address token_b;
    uint256 maxAmountInA;
    uint256 maxAmountInB;

    bool fromInternalBalance;

    uint256 init_fee = Harness_getACollectedFee(token_checked);

    Harness_doubleJoinPool(e, poolId, sender, recipient, token_a, token_b, maxAmountInA, maxAmountInB, fromInternalBalance);
    uint256 final_fee = Harness_getACollectedFee(token_checked);

    assert final_fee >= init_fee, "joinPool should never lose the vault tax money";
}

rule harmlessJoinPoolGeneralMinimal {
    env e;
    address token_checked;

    bytes32 poolId;
    require !Harness_poolIsTwoTokens(poolId);

    address sender;
    legalAddress(sender);
    noIllegalRelayer(sender);

    address recipient;

    address token_a;
    address token_b;
    uint256 maxAmountInA;
    uint256 maxAmountInB;

    bool fromInternalBalance;

    uint256 init_vault_balance = getTokenBalance(currentContract, token_checked);
    uint256 init_fee = Harness_getACollectedFee(token_checked);
    uint256 init_tot_balance = init_vault_balance + init_fee;

    Harness_doubleJoinPool(e, poolId, sender, recipient, token_a, token_b, maxAmountInA, maxAmountInB, fromInternalBalance);

    uint256 fin_vault_balance = getTokenBalance(currentContract, token_checked);
    uint256 fin_fee = Harness_getACollectedFee(token_checked);
    uint256 fin_tot_balance = init_vault_balance + init_fee;

    assert fin_tot_balance >= init_tot_balance, "joinPool should never lose the vault money";
}

rule harmlessJoinPoolTwoTokens {
    env e;
    address token_checked;

    bytes32 poolId;
    require Harness_poolIsTwoTokens(poolId);

    address sender;
    legalAddress(sender);
    noIllegalRelayer(sender);

    address recipient;

    address token_a;
    address token_b;
    uint256 maxAmountInA;
    uint256 maxAmountInB;

    bool fromInternalBalance;

    uint256 init_vault_balance = getTokenBalance(currentContract, token_checked);
    uint256 init_fee = Harness_getACollectedFee(token_checked);
    uint256 init_tot_balance = init_vault_balance + init_fee;

    Harness_doubleJoinPool(e, poolId, sender, recipient, token_a, token_b, maxAmountInA, maxAmountInB, fromInternalBalance);
 
    uint256 fin_vault_balance = getTokenBalance(currentContract, token_checked);
    uint256 fin_fee = Harness_getACollectedFee(token_checked);
    uint256 fin_tot_balance = init_vault_balance + init_fee;

    assert fin_tot_balance >= init_tot_balance, "joinPool should never lose the vault money";
}

rule noJoinPoolUserProfit {
    env e;
    address token_checked;

    bytes32 poolId;
    legalPool(poolId);

    address sender;
    legalAddress(sender);
    noIllegalRelayer(sender);

    address recipient;

    address token_a;
    address token_b;
    uint256 maxAmountInA;
    uint256 maxAmountInB;

    bool fromInternalBalance;

    uint256 init_balance = getTokenBalance(sender, token_checked);

    Harness_doubleJoinPool(e, poolId, sender, recipient, token_a, token_b, maxAmountInA, maxAmountInB, fromInternalBalance);
    uint256 final_balance = getTokenBalance(sender, token_checked);

    assert final_balance <= init_balance, "The sender should not profit for joining a pool";
}

rule joinPoolCappedUserLoss {
    env e;

    bytes32 poolId;

    address sender;
    address recipient;

    address token;
    uint256 maxAmountIn;

    bool fromInternalBalance;

    uint256 init_erc_balance = getTokenBalance(sender, token);
    uint256 init_internal_balance = _getInternalBalance(sender, token);

    Harness_singleJoinPool(e, poolId, sender, recipient, token, maxAmountIn, fromInternalBalance);
    uint256 final_erc_balance = getTokenBalance(sender, token);
    uint256 final_internal_balance = _getInternalBalance(sender, token);

    mathint erc_loss = init_erc_balance - final_erc_balance;
    mathint internal_loss = init_internal_balance - final_internal_balance;
    mathint total_loss = erc_loss + internal_loss;

    assert total_loss <= maxAmountIn, "The sender's losses are capped at maxAmountIn";
}

/*
//Rule times out
rule exitPoolProfitabilityTwoTokensPool {
    env e;
    address token_checked;

    bytes32 poolId;
    require Harness_poolIsTwoTokens(poolId);

    address sender;
    address recipient;

    address token_a;
    address token_b;
    uint256 minAmountOutA;
    uint256 minAmountOutB;

    bool toInternalBalance;

    uint256 init_fee = Harness_getACollectedFee(token_checked);

    Harness_doubleExitPool(e, poolId, sender, recipient, token_a, token_b, minAmountOutA, minAmountOutB, 
                           toInternalBalance);
    uint256 final_fee = Harness_getACollectedFee(token_checked);

    // assert final_fee >= init_fee, "exitPool should never lose the vault tax money";
    assert false;
}
*/

/* The rule below is a weaker form of rules to follow. It it useful for debugging if the more complex rules fail.
*/
rule exitPoolProfitabilityGeneralMinimalPool {
    env e;
    address token_checked;

    bytes32 poolId;
    require !Harness_poolIsTwoTokens(poolId);

    address sender;
    address recipient;

    address token_a;
    address token_b;
    uint256 minAmountOutA;
    uint256 minAmountOutB;

    bool toInternalBalance;

    uint256 init_fee = Harness_getACollectedFee(token_checked);

    Harness_doubleExitPool(e, poolId, sender, recipient, token_a, token_b, minAmountOutA, minAmountOutB, 
                           toInternalBalance);
    uint256 final_fee = Harness_getACollectedFee(token_checked);

    assert final_fee >= init_fee, "exitPool should never lose the vault tax money";
}

rule exitPoolMinUserProfit {
    env e;

    bytes32 poolId;
    require Harness_poolIsGeneral(poolId);

    address sender;
    address recipient;
    require recipient != currentContract;  // If the recipient is the current contract, current contract's balance stays the same - no profit at all...

    address token;
    uint256 minAmountOut;

    bool toInternalBalance;

    uint256 init_erc_balance = getTokenBalance(recipient, token);
    uint256 init_internal_balance = _getInternalBalance(recipient, token);

    Harness_singleExitPool(e, poolId, sender, recipient, token, minAmountOut, toInternalBalance);
    uint256 final_erc_balance = getTokenBalance(recipient, token);
    uint256 final_internal_balance = _getInternalBalance(recipient, token);

    mathint erc_profit = final_erc_balance - init_erc_balance;
    mathint internal_profit = final_internal_balance - init_internal_balance;
    mathint total_profit = erc_profit + internal_profit;

    assert toInternalBalance => total_profit >= minAmountOut, 
        "exitPool's recipient's profits are bounded from below at minAmountOut, and no taxes are charges when we deposit to an internal balance";
    
}
