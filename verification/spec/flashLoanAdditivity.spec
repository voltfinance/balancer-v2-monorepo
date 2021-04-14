methods {
    getTokenBalance(address, address) returns uint256 envfree
    receiveFlashLoan(address[], uint256[], uint256[], bytes) => DISPATCHER(true)

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

    nop() => NONDET
}

rule flashLoanProfitability {
    address receiver;
    env e;
    address token_checked;

    address token_a;
    address token_b;
    uint256 amount_a;
    uint256 amount_b;

    uint256 init_balance = getTokenBalance(currentContract, token_checked);
    Harness_doubleFlashLoan(e, receiver, token_a, token_b, amount_a, amount_b);
    uint256 final_balance = getTokenBalance(currentContract, token_checked);

    assert final_balance >= init_balance, "a flash loan should never lose the vault money";
}

rule flashLoanAdditivity {

    address receiver;
    env e;

    address token_a;
    address token_b;

    uint256 amount_a;
    uint256 amount_b;

    storage init = lastStorage;
    Harness_singleFlashLoan(e, receiver, token_a, amount_a);
    Harness_singleFlashLoan(e, receiver, token_b, amount_b);
    uint256 token_a_vault_balance_1 = getTokenBalance(currentContract, token_a);

    Harness_doubleFlashLoan(e, receiver, token_a, token_b, amount_a, amount_b) at init;
    uint256 token_a_vault_balance_2 = getTokenBalance(currentContract, token_a);

    assert token_a_vault_balance_1 >= token_a_vault_balance_2, "vault should not lose money from splitting flash loans";
}