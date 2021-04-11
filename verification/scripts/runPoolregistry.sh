certoraRun verification/harness/PoolRegistryHarness.sol \
    --verify PoolRegistryHarness:verification/spec/poolregistry.spec \
    --solc solc7.6 \
    --cache balancerPoolRegistryBv \
    --settings -useBitVectorTheory,-ruleSanityChecks \
    --msg "Pool registry, bitvector analysis, pool id/address conversions invertible"
