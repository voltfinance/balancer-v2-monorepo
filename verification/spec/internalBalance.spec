methods {
    _getInternalBalance(address, address) returns uint256 envfree
    Harness_isVaultRelayer() returns bool envfree

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

rule internalBalanceChanges {
    address user;
    address token;
    uint256 balance_pre = _getInternalBalance(user, token);

    method f;
    // require f.selector != UserBalanceOp();

    calldataarg a;
    env e;
    f(e,a);

    uint256 balance_post = _getInternalBalance(user, token);

    // if (f.selector == 
    //         depositToInternalBalance(address, address[], uint256[], address).selector ||
    //     f.selector == exitPool(bytes32,address,address,address[],uint256[],bool,bytes).selector) {
    //     assert balance_post >= balance_pre, "depositToInternalBalance() can only increase the balance";
    // } else if (f.selector == 
    //                 withdrawFromInternalBalance(address, address[], uint256[], address).selector ||
    //            f.selector == joinPool(bytes32,address,address,address[],uint256[],bool,bytes).selector){
    //     assert balance_post <= balance_pre, 
    //         "withdrawFromInternalBalance() and joinPool() can only decrease the balance";
    // } else {
    //     assert balance_post == balance_pre, "this method should not affect the internal balance";
    // }
    assert balance_post == balance_pre, "this method should not affect the internal balance";
}

rule only_authorizer_can_decrease_internal_balance {
    address user;
    address token;
    uint256 init_balance = _getInternalBalance(user, token);

    method f;
    env e;
    calldataarg a;
    f(e, a);

    uint256 final_balance = _getInternalBalance(user, token);
    mathint balance_diff = final_balance - init_balance;
    bool authorized = Harness_isAuthenticatedByUser(e, user);

    assert balance_diff < 0 => authorized, "only an authorized message sender can decrease a user's internal balance";
}

invariant vault_has_no_relayers() !Harness_isVaultRelayer() {
    preserved changeRelayerAllowance(address user, address relayer, bool b) with (env e) {
        require e.msg.sender != currentContract;  // It is an external function
    }
}
