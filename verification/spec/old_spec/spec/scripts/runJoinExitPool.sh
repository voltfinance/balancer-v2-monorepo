certoraRun spec/harness/joinExitPoolHarness.sol:JoinExitPoolHarness spec/DummyERC20.sol spec/DummyERC20B.sol \
  --verify JoinExitPoolHarness:spec/joinExitPool.spec \
  --solc solc7.6 \
  --cache balancerAdditivity \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-b=2 \
  --staging --msg "run all join exit pool rules"