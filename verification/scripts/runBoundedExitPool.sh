cp contracts/vault/balances/BalanceAllocation.sol contracts/vault/balances/BalanceAllocation.sol.orig
cp verification/harness/SimpleBalanceAllocation.sol contracts/vault/balances/BalanceAllocation.sol
certoraRun verification/harness/joinExitPoolHarness.sol:JoinExitPoolHarness verification/harness/DummyERC20.sol verification/harness/DummyERC20B.sol \
  --verify JoinExitPoolHarness:verification/spec/boundedExitPool.spec \
  --solc solc7.6 \
  --cache balancerBoundedExit \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-b=2,-t=1200 \
  --staging shelly/optimizerWeeklyTesting --msg "running all rules for bounded exit pool, with t=1200"
cp contracts/vault/balances/BalanceAllocation.orig contracts/vault/balances/BalanceAllocation.sol