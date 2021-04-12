certoraRun verification/harness/internalBalanceHarness.sol \
  --verify internalBalanceHarness:verification/spec/internalBalance.spec \
  --solc solc7.6 \
  --cache balancerInternalBalance \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-copyLoopUnroll=2,-b=2 \
  --staging --msg "checking internalBalance"