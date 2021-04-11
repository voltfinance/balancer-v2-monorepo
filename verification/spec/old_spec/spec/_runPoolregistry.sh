certoraRun spec/harness/PoolRegistryHarness.sol \
    --verify PoolRegistryHarness:spec/poolregistry.spec \
    --solc solc7.5 \
    --cache balancerPoolRegistryBv \
    --settings -useBitVectorTheory \
    --cloud --msg "Pool registry, bitvector analysis, pool id/address conversions invertible"