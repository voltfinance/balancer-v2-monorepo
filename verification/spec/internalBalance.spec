methods {
    Harness_getAnInternalBalance(address, address) returns uint256 envfree 
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
    uint256 balance_pre = Harness_getAnInternalBalance(user, token);

    method f;
    require f.selector != manageUserBalance((uint8,address,uint256,address,address)[]).selector;
    require f.selector != swap((bytes32,uint8,address,address,uint256,bytes),(address,bool,address,bool),uint256,uint256).selector;
    require f.selector != batchSwap(uint8,(bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256).selector;

    calldataarg a;
    env e;
    f(e, a);

    uint256 balance_post = Harness_getAnInternalBalance(user, token);

    if (f.selector == exitPool(bytes32,address,address,(address[],uint256[],bytes,bool)).selector) {
        assert balance_post >= balance_pre, "this method cannot decrease internal balance";
    } else if (f.selector == joinPool(bytes32,address,address,(address[],uint256[],bytes,bool)).selector) {
        assert balance_post <= balance_pre, "this method cannot increase internal balance";
    } else {
        assert balance_post == balance_pre, "this method should not affect the internal balance";
    }
    
}

rule only_authorizer_can_decrease_internal_balance {
    address user;
    address token;
    uint256 init_balance = Harness_getAnInternalBalance(user, token);

    method f;
    env e;
    calldataarg a;
    f(e, a);

    uint256 final_balance = Harness_getAnInternalBalance(user, token);
    mathint balance_diff = final_balance - init_balance;
    bool authorized = Harness_isAuthenticatedByUser(e, user);

    assert balance_diff < 0 => authorized, "only an authorized message sender can decrease a user's internal balance";
}

invariant vault_has_no_relayers() !Harness_isVaultRelayer() {
    preserved changeRelayerAllowance(address user, address relayer, bool b) with (env e) {
        require e.msg.sender != currentContract;  // It is an external function
    }
}
