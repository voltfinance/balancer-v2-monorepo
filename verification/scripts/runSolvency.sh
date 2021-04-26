certoraRun verification/harness/solvencyHarness.sol contracts/vault/ProtocolFeesCollector.sol \
  verification/harness/DummyERC20.sol verification/harness/FlashLoanReceiver.sol:Borrower \
  verification/harness/WETH.sol \
  --verify solvencyHarness:verification/spec/solvency.spec \
  --link solvencyHarness:_protocolFeesCollector=ProtocolFeesCollector \
  --link solvencyHarness:_weth=WETH \
  --solc solc7.6 \
  --cache balancerSolvency \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-copyLoopUnroll=2,-b=2,-nonIterEdgeBlocksRemoval,-t=1200 \
  --rule sum_of_internal_balance_less_than_vault_funds \
  --staging --msg "sum_of_internal_balance_less_than_vault_funds with t=1200"