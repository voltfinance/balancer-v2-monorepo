using DummyERC20 as ERC20

methods {
    hasApprovedRelayer(address, address) returns bool envfree
    Harness_has_valid_signature(address) returns bool envfree
    Harness_vaultEthBalance() envfree
    Harness_get_receive_asset_counter(address) returns uint256 envfree

    ERC20.myAddress() returns address envfree
    transfer(address, uint256) returns bool envfree => DISPATCHER(true)
    transferFrom(address, address, uint256) returns bool envfree => DISPATCHER(true)
    balanceOf(address) returns uint256 envfree => DISPATCHER(true)
    ERC20.totalSupply() returns uint256 envfree

    // pool interface commands
    0xd5c096c4 => NONDET // onJoinPool
    0x74f3b009 => NONDET // onExitPool

    // Bottom two lines are probably useless
    // 0x223b57e5 => NONDET // onSwapGivenOut
    // 0x9588c193 => NONDET // onSwapGivenIn

    0xf84d066e => NONDET // queryBatchSwap()

    0x9d2c110c => NONDET // onSwap hook of a minimal swap info pool
    0x01ec954a => NONDET // onSwap general pool
    nop() => NONDET
    deposit() => DISPATCHER(true)
    withdraw(uint256) => DISPATCHER(true)

    receiveFlashLoan(address[], uint256[], uint256[], bytes) => DISPATCHER(true)
}

/*
    The swaps are expensive functions, so during rule development, these can be handy:
    // require f.selector != 0x45eb8830; //batchSwapGivenOut
    // require f.selector != 0x77c6b2c9; //batchSwapGivenIn
*/

function noIllegalRelayer(address suspect) {
    require !hasApprovedRelayer(currentContract, suspect);
    require !hasApprovedRelayer(ERC20, suspect);
   /* require !hasApprovedRelayer(weth, suspect);
    require !hasApprovedRelayer(borrower, suspect);
    require !hasApprovedRelayer(feesCollector, suspect);*/
    require !Harness_has_valid_signature(currentContract);
    require !Harness_has_valid_signature(ERC20);
   /* require !Harness_has_valid_signature(weth);
    require !Harness_has_valid_signature(borrower);
    require !Harness_has_valid_signature(feesCollector);*/
}

function legalAddress(address suspect) {
    require suspect != currentContract;
    require suspect != ERC20;
    /*require suspect != weth;
    require suspect != borrower;
    require suspect != feesCollector;*/
}


rule vault_gets_no_eth {
    uint256 init_eth = Harness_vaultEthBalance();

    method f;

    /*
    Limiting f because of timeouts
    batchSwapGivenOut((bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256)
    batchSwapGivenIn((bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256)
    */
    require f.selector != 0x45eb8830; //batchSwapGivenOut
    require f.selector != 0x77c6b2c9; //batchSwapGivenIn

    require f.selector != 0x945bcec9; // do not check batchSwap
    env e;
    legalAddress(e.msg.sender);
    calldataarg a;
    f(e, a);

    uint256 final_eth = Harness_vaultEthBalance();

    assert init_eth == final_eth, "the vault cannot gain any ETH";
}

rule receive_asset_called_at_most_once_per_token {
    address token = ERC20.myAddress();
    uint256 init_count = Harness_get_receive_asset_counter(token);

    method f;

    /*
    Limiting f because of timeouts
    batchSwapGivenOut((bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256)
    batchSwapGivenIn((bytes32,uint256,uint256,uint256,bytes)[],address[],(address,bool,address,bool),int256[],uint256)
    */
    require f.selector != 0x45eb8830; //batchSwapGivenOut
    require f.selector != 0x77c6b2c9; //batchSwapGivenIn

    env e;
    calldataarg a;
    f(e, a);

    uint256 final_count = Harness_get_receive_asset_counter(token);

    uint256 count_difference = final_count - init_count;
    assert count_difference < 2, "receiveAsset() can only be called once per token per transaction";
}
