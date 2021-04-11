certoraRun verification/harness/simplifiedVaultHarness.sol \
  --verify simplifiedVaultHarness:verification/spec/general_spec.spec \
  --solc solc7.6 \
  --cache balancerGeneral \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-copyLoopUnroll=2,-b=2 \
  --staging --msg "run general spec rule changeRelayerAllowanceIntegrity"