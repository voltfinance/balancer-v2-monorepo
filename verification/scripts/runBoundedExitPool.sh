certoraRun verification/harness/joinExitPoolHarness.sol:JoinExitPoolHarness verification/harness/DummyERC20.sol verification/harness/DummyERC20B.sol \
  contracts/vault/ProtocolFeesCollector.sol verification/harness/WETH.sol \
  --verify JoinExitPoolHarness:verification/spec/boundedExitPool.spec \
  --link JoinExitPoolHarness:_protocolFeesCollector=ProtocolFeesCollector \
  --link JoinExitPoolHarness:_weth=WETH \
  --solc solc7.6 \
  --cache balancerBoundedExit \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-b=2,-t=1200 \
  --rule vault_loses_on_exit_pool \
  --staging shelly/optimizerWeeklyTesting --msg "bounded exit pool -r vault_loses_on_exit_pool more simplifications"
