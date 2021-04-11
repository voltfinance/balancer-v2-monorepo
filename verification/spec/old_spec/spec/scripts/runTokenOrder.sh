certoraRun spec/harness/tokenOrderHarness.sol \
  --verify tokenOrderHarness:spec/tokenOrder.spec \
  --solc solc7.6 \
  --cache balancerTokenOrder \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-copyLoopUnroll=2,-b=2 \
  --staging --msg "all token order functions"