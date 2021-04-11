methods {
    toPoolId(address pool, uint specialization, uint80 nonce) returns (bytes32) envfree 

    getPoolAddress(bytes32 poolId) returns (address) envfree
}

rule toPoolIdAndThenGetPoolAddressIsNeutral {
    address pool1;
    uint specialization;
    uint80 nonce;

    bytes32 poolId = toPoolId(pool1, specialization, nonce);

    address pool2 = getPoolAddress(poolId);

    assert pool1 == pool2, "A pools address should be recontructable from the pool's id";
}
