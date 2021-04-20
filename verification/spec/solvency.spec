using DummyERC20 as ERC20

methods {

    Harness_getACollectedFee(address) returns uint256 envfree
    _getInternalBalance(address, address) returns uint256 envfree

    Harness_poolIsGeneral(bytes32) envfree
    Harness_getGeneralPoolTotalBalance(bytes32, address) returns uint256 envfree
    Harness_get_pool_cash_like_exit_pool(bytes32, address) returns uint256 envfree

    Harness_isVaultRelayer(address) returns bool envfree

    ERC20.myAddress() returns address envfree
    // ERC20.totalSupply() returns uint256 envfree

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

rule vault_never_changes_total_supply {
    uint256 supply_pre = ERC20.totalSupply();

    env e;
    require e.msg.sender != currentContract;
    calldataarg a;
    method f;

    require f.selector != 0x945bcec9; // batchswap
    f(e, a);

    uint256 supply_post = ERC20.totalSupply();
    assert supply_post == supply_pre;
}

///////// Solvency step 1

/* represent the sum of _internalTokenBalance of a specific token for all accounts */
// mapping(address => mapping(IERC20 => uint256)) private _internalTokenBalance;
ghost internalBalanceSumPerToken(uint) returns uint256 {
    init_state axiom forall address token. internalBalanceSumPerToken(token) == 0; // initialization
}

hook Sstore _internalTokenBalance[KEY uint account][KEY uint token] uint balance (uint oldBalance) STORAGE {
	havoc internalBalanceSumPerToken assuming internalBalanceSumPerToken@new(token) == internalBalanceSumPerToken@old(token) + balance - oldBalance &&
		(forall uint t. t != token => internalBalanceSumPerToken@new(t) == internalBalanceSumPerToken@old(t));
}

// token.balanceOf(currentContract) >= internalBalanceSumPerToken(token)

rule sum_of_internal_balance_less_than_vault_funds {
    address token = ERC20.myAddress();
    uint256 internal_sum_pre = internalBalanceSumPerToken(token);
    uint256 vault_balance_pre = ERC20.balanceOf(currentContract);
    require internal_sum_pre <= vault_balance_pre;

    env e;
    require e.msg.sender != currentContract;
    require !Harness_isVaultRelayer(e.msg.sender);  // proven before

    calldataarg a;
    method f;

    /*
    Limiting f because of timeouts
    batchSwapGivenOut((bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256)
    batchSwapGivenIn((bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256)
    */
    require f.selector != 0x945bcec9; // batchswap
    require f.selector != Harness_doubleJoinPool(bytes32,address,address,address,address,uint256,uint256,bool).selector;
    require f.selector != Harness_doubleExitPool(bytes32,address,address,address,address,uint256,uint256,bool).selector;

    // if f.selector == exitPool(bytes32,address,address,address[],uint256[],bool,bytes).selector { 

    //     bytes32 poolId;
    //     require Harness_poolIsGeneral(poolId);
    //     uint256 pool_balance_pre = Harness_get_pool_cash_like_exit_pool(poolId, token);
    //     require vault_balance_pre >= pool_balance_pre + internal_sum_pre;

    //     address sender;
    //     address recipient;
    //     address token_a;
    //     address token_b;
    //     uint256 maxAmountInA;
    //     uint256 maxAmountInB;
    //     bool fromInternalBalance;
    //     Harness_doubleJoinPool(e, poolId, sender, recipient, token_a, token_b, maxAmountInA, maxAmountInB, fromInternalBalance);

    // } else {

    //     f(e, a);

    // }
    f(e, a);

    uint256 internal_sum_post = internalBalanceSumPerToken(token);
    uint256 vault_balance_post = ERC20.balanceOf(currentContract);
    assert internal_sum_post <= vault_balance_post, "the sum of internal balances cannot be higher than all vault funds";
}


// rule sum_of_internal_balance_and_fees_less_than_vault_funds {
//     address token = ERC20.myAddress();

//     uint256 internal_sum_pre = internalBalanceSumPerToken(token);
//     uint256 fees_pre = Harness_getACollectedFee(token);
//     mathint min_vault_balance = fees_pre + internal_sum_pre;

//     uint256 vault_balance_pre = ERC20.balanceOf(currentContract);
//     require min_vault_balance <= vault_balance_pre;

//     env e;
//     require e.msg.sender != currentContract;
//     require !Harness_isVaultRelayer(e.msg.sender);  // proven before

//     calldataarg a;
//     method f;

//     /*
//     Limiting f because of timeouts
//     batchSwapGivenOut((bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256)
//     batchSwapGivenIn((bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256)
//     */
//     require f.selector != 0x45eb8830; //batchSwapGivenOut
//     require f.selector != 0x77c6b2c9; //batchSwapGivenIn
//     require f.selector != Harness_doubleJoinPool(bytes32,address,address,address,address,uint256,uint256,bool).selector;
//     require f.selector != Harness_doubleExitPool(bytes32,address,address,address,address,uint256,uint256,bool).selector;

//     if f.selector == withdrawFromPoolBalance(bytes32, address, uint256).selector {

//         bytes32 poolId;
//         require Harness_poolIsGeneral(poolId);

//         uint256 pool_balance_pre = Harness_getGeneralPoolTotalBalance(poolId, token);
//         require vault_balance_pre >= pool_balance_pre + min_vault_balance;
//         uint256 amount;
//         withdrawFromPoolBalance(e, poolId, token, amount);

//     } else if f.selector == joinPool(bytes32,address,address,address[],uint256[],bool,bytes).selector { 

//         bytes32 poolId;
//         require Harness_poolIsGeneral(poolId);
//         uint256 pool_balance_pre = Harness_get_pool_cash_like_exit_pool(poolId, token);
//         require vault_balance_pre >= pool_balance_pre + min_vault_balance;

//         address sender;
//         address recipient;
//         address token_a;
//         address token_b;
//         uint256 maxAmountInA;
//         uint256 maxAmountInB;
//         bool fromInternalBalance;
//         Harness_doubleJoinPool(e, poolId, sender, recipient, token_a, token_b, maxAmountInA, maxAmountInB, fromInternalBalance);

//     } else if f.selector == exitPool(bytes32,address,address,address[],uint256[],bool,bytes).selector { 

//         bytes32 poolId;
//         require Harness_poolIsGeneral(poolId);
//         uint256 pool_balance_pre = Harness_get_pool_cash_like_exit_pool(poolId, token);
//         require vault_balance_pre >= pool_balance_pre + min_vault_balance;

//         address sender;
//         address recipient;
//         address token_a;
//         address token_b;
//         uint256 maxAmountInA;
//         uint256 maxAmountInB;
//         bool fromInternalBalance;
//         Harness_doubleJoinPool(e, poolId, sender, recipient, token_a, token_b, maxAmountInA, maxAmountInB, fromInternalBalance);

//     } else {

//         f(e, a);

//     }

//     uint256 internal_sum_post = internalBalanceSumPerToken(token);
//     uint256 fees_post = Harness_getACollectedFee(token);
//     uint256 vault_balance_post = ERC20.balanceOf(currentContract);
//     assert internal_sum_post + fees_post <= vault_balance_post, "the sum of internal balances plus collected fees cannot be higher than all vault funds";
// }

// rule only_one_pool_balance_changes_if_not_swap {
//     address token = ERC20.myAddress();

//     bytes32 pool_a;
//     require Harness_poolIsGeneral(pool_a);
//     uint256 pool_a_balance_pre = Harness_getGeneralPoolTotalBalance(pool_a, token);

//     bytes32 pool_b;
//     require Harness_poolIsGeneral(pool_b);
//     uint256 pool_b_balance_pre = Harness_getGeneralPoolTotalBalance(pool_b, token);

//     method f;
//     /*
//     Limiting f because of timeouts
//     batchSwapGivenOut((bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256)
//     batchSwapGivenIn((bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256)
//     */
//     require f.selector != 0x45eb8830; //batchSwapGivenOut
//     require f.selector != 0x77c6b2c9; //batchSwapGivenIn
//     require f.selector != Harness_doubleJoinPool(bytes32,address,address,address,address,uint256,uint256,bool).selector;
//     require f.selector != Harness_doubleExitPool(bytes32,address,address,address,address,uint256,uint256,bool).selector;

//     env e;
//     require e.msg.sender != currentContract;
//     require !Harness_isVaultRelayer(e.msg.sender);  // proven before

//     calldataarg a;

//     f(e, a);

//     uint256 pool_a_balance_post = Harness_getGeneralPoolTotalBalance(pool_a, token);
//     uint256 pool_b_balance_post = Harness_getGeneralPoolTotalBalance(pool_b, token);
    
//     bool pool_a_changed = pool_a_balance_post != pool_a_balance_pre;
//     bool pool_b_changed = pool_b_balance_post != pool_b_balance_pre;
//     assert pool_a_changed && pool_b_changed => pool_a == pool_b;
// }
