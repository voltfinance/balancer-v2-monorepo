certoraRun verification/spec/harness/simplifiedVaultHarness.sol \
  --verify simplifiedVaultHarness:spec/general_spec.spec \
  --solc solc7.6 \
  --cache balancerGeneral \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-copyLoopUnroll=2,-b=2 \
  --staging --msg "run general spec"