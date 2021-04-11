certoraRun verification/harness/simplifiedVaultHarness.sol contracts/vault/ProtocolFeesCollector.sol\
  --verify simplifiedVaultHarness:verification/spec/general_spec.spec \
  --link simplifiedVaultHarness:_protocolFeesCollector=ProtocolFeesCollector \
  --solc solc7.6 \
  --cache balancerGeneral \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-copyLoopUnroll=2,-b=2 \
  --staging --msg "run general spec rule increasingFees with linking the protocol fess collector"