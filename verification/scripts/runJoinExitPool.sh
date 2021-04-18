certoraRun verification/harness/joinExitPoolHarness.sol:JoinExitPoolHarness verification/harness/DummyERC20.sol verification/harness/DummyERC20B.sol \
  --verify JoinExitPoolHarness:verification/spec/joinExitPool.spec \
  --solc solc7.6 \
  --cache balancerAdditivity \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-b=2 \
  --staging shelly/optimizerWeeklyTesting --msg "run all join exit pool rules"