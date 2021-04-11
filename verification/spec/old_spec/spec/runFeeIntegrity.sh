certoraRun spec/FeeHarness.sol \
  --verify FeeHarness:spec/feeIntegrity.spec \
  --solc solc7.6 \
  --cache balancerFeeIntegrity \
  --settings -ignoreViewFunctions,-assumeUnwindCond \
  --staging --msg "Balancer Fee Integrity"
