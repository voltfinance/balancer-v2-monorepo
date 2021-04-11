certoraRun spec/harness/mutabilityHarness.sol \
  --verify mutabilityHarness:spec/queryBatchSwapIsView.spec \
  --solc solc7.6 \
  --cache balancerMutability \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-copyLoopUnroll=2,-b=2 \
  --staging --msg "checking queryBatchSwapIsView"