methods {
    _getInternalBalance(address, address) returns uint256 envfree
    getTokenBalance(address, address) returns uint256 envfree
    Harness_getGeneralPoolTotalBalance(bytes32, address) returns uint256 envfree
    Harness_poolIsGeneral(bytes32) returns bool envfree

    Harness_get_pool_cash_like_exit_pool(bytes32, address) returns uint256 envfree

    transfer(address, uint256) => DISPATCHER(true)
    transferFrom(address, address, uint256) => DISPATCHER(true)
    balanceOf(address) => DISPATCHER(true)

    0xd5c096c4 => NONDET // onJoinPool
    0x74f3b009 => NONDET // onExitPool
}

rule vault_loses_on_exit_pool {
    env e;

    bytes32 poolId;
    require Harness_poolIsGeneral(poolId); // Fake pool anyway

    address sender;
    address recipient;

    address token;
    uint256 minAmountOut;

    bool toInternalBalance;

    uint256 init_tot_balance = Harness_getGeneralPoolTotalBalance(poolId, token);

    Harness_singleExitPool(e, poolId, sender, recipient, token, minAmountOut, toInternalBalance);

    uint256 final_tot_balance = Harness_getGeneralPoolTotalBalance(poolId, token);

    assert final_tot_balance <= init_tot_balance, "A Pool's token balance always decreases after an exit (potentially by 0).";
}

rule exit_pool_upper_bound {
    env e;

    bytes32 poolId;
    require Harness_poolIsGeneral(poolId);  // Fake pool anyway

    address sender;
    address recipient;
    address token;
    uint256 minAmountOut;
    bool toInternalBalance;

    uint256 init_erc_balance = getTokenBalance(recipient, token);
    uint256 init_internal_balance = _getInternalBalance(recipient, token);
    uint256 init_pool_balance = Harness_get_pool_cash_like_exit_pool(poolId, token);


    Harness_singleExitPool(e, poolId, sender, recipient, token, minAmountOut, toInternalBalance);

    uint256 final_erc_balance = getTokenBalance(recipient, token);
    uint256 final_internal_balance = _getInternalBalance(recipient, token);
    uint256 erc_profit = final_erc_balance - init_erc_balance;
    uint256 internal_profit = final_internal_balance - init_internal_balance;
    uint256 total_profit = erc_profit + internal_profit;

    uint256 final_pool_balance = Harness_get_pool_cash_like_exit_pool(poolId, token);

    assert total_profit <= init_pool_balance, "A user cannot gain more money than the total amount in the General Pool when exiting";
}