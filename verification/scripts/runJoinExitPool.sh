certoraRun verification/harness/joinExitPoolHarness.sol:JoinExitPoolHarness verification/harness/DummyERC20.sol verification/harness/DummyERC20B.sol \
  verification/harness/WETH.sol contracts/vault/ProtocolFeesCollector.sol \
  --verify JoinExitPoolHarness:verification/spec/joinExitPool.spec \
  --link JoinExitPoolHarness:_protocolFeesCollector=ProtocolFeesCollector \
  --link JoinExitPoolHarness:_weth=WETH \
  --solc solc7.6 \
  --cache balancerAdditivity \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-b=2 \
  --rule harmlessJoinPoolTwoTokens \
  --staging shelly/optimizerWeeklyTesting --msg "joinExitPool r harmlessJoinPoolTwoTokens with correct balance check"