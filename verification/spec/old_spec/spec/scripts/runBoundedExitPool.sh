cp contracts/vault/balances/SimpleBalanceAllocation.sol contracts/vault/balances/BalanceAllocation.sol
certoraRun spec/harness/joinExitPoolHarness.sol:JoinExitPoolHarness spec/DummyERC20.sol spec/DummyERC20B.sol \
  --verify JoinExitPoolHarness:spec/boundedExitPool.spec \
  --solc solc7.6 \
  --cache balancerBoundedExit \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-b=2,-t=1200 \
  --staging --msg "running all rules for bounded exit pool, with t=1200"
cp contracts/vault/balances/BalanceAllocation.orig contracts/vault/balances/BalanceAllocation.sol