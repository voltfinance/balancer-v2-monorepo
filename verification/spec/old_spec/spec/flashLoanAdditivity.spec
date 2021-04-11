methods {
    getTokenBalance(address, address) returns uint256 envfree
    balanceOf(address) => DISPATCHER(true)
    receiveFlashLoan(address[], uint256[], uint256[], bytes) => DISPATCHER(true)
    transfer(address, uint256) => DISPATCHER(true)
    transferFrom(address, address, uint256) => DISPATCHER(true)
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