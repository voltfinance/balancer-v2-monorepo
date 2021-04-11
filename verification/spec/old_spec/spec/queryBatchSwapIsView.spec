methods {
    getStorageBytes32(bytes32) returns bytes32 envfree
}

rule queryBatchSwapIsView {
    bytes32 position;
    bytes32 data_pre = getStorageBytes32(position);

    env e;
    calldataarg a;
    queryBatchSwap(e, a);

    bytes32 data_post = getStorageBytes32(position);

    assert data_pre == data_post, "queryBatchSwap should behave like a view function";
}