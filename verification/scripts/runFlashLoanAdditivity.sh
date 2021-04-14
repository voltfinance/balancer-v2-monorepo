certoraRun verification/harness/flashLoanHarness.sol contracts/vault/ProtocolFeesCollector.sol verification/harness/DummyERC20.sol \
  verification/harness/FlashLoanReceiver.sol:Borrower verification/harness/WETH.sol \
  --verify flashLoanHarness:verification/spec/flashLoanAdditivity.spec \
  --link flashLoanHarness:_protocolFeesCollector=ProtocolFeesCollector \
  --link flashLoanHarness:_weth=WETH \
  --solc solc7.6 \
  --cache balancerAdditivity \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-b=3 \
  --staging --msg "flash loan additivity"
    # -b must be >= 3 to pass sanity 