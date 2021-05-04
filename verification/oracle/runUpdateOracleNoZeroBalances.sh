certoraRun verification/oracle/NoUpdateOracleRevertHarness.sol verification/harness/joinExitPoolHarness.sol:JoinExitPoolHarness \
  contracts/vault/ProtocolFeesCollector.sol verification/harness/DummyERC20.sol verification/harness/WETH.sol \
  verification/harness/FlashLoanReceiver.sol:Borrower verification/harness/DummyERC20B.sol \
  --link JoinExitPoolHarness:_protocolFeesCollector=ProtocolFeesCollector \
  --link JoinExitPoolHarness:_weth=WETH \
  --verify JoinExitPoolHarness:verification/oracle/NoOracleZeroBalances.spec \
  --solc solc7.6 \
  --settings -ruleSanityChecks,-assumeUnwindCond,-b=3,-ignoreViewFunctions,-recursionEntryLimit=6,-copyLoopUnroll=3 \
  --cache balancer_oracle_revert \
  --rule oracle_balance_positive_after_join \
  --staging --msg "rule oracle_balance_positive_after_join, smart fake fixed point"
