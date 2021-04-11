methods {
    Harness_getAnInternalBalance(address, address) returns uint256 envfree
    Harness_isVaultRelayer() returns bool envfree
}

rule internalBalanceChanges {
    address user;
    address token;
    uint256 balance_pre = Harness_getAnInternalBalance(user, token);

    method f;
    require f.selector != transferInternalBalance(address, address[], uint256[], address[]).selector;
    // require f.selector != batchSwapGivenOut((bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256).selector;
    require f.selector != 0x77c6b2c9;
    // require f.selector != batchSwapGivenIn((bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256).selector;
    require f.selector != 0x45eb8830;

    calldataarg a;
    env e;
    f(e,a);

    uint256 balance_post = Harness_getAnInternalBalance(user, token);

    if (f.selector == 
            depositToInternalBalance(address, address[], uint256[], address).selector ||
        f.selector == exitPool(bytes32,address,address,address[],uint256[],bool,bytes).selector) {
        assert balance_post >= balance_pre, "depositToInternalBalance() can only increase the balance";
    } else if (f.selector == 
                    withdrawFromInternalBalance(address, address[], uint256[], address).selector ||
               f.selector == joinPool(bytes32,address,address,address[],uint256[],bool,bytes).selector){
        assert balance_post <= balance_pre, 
            "withdrawFromInternalBalance() and joinPool() can only decrease the balance";
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
    preserved changeRelayerAllowance(address a, bool b) with (env e) {
        require e.msg.sender != currentContract;  // It is an external function
    }
}
