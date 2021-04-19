certoraRun verification/harness/flashLoanHarness.sol contracts/vault/ProtocolFeesCollector.sol verification/harness/DummyERC20.sol \
  verification/harness/FlashLoanReceiver.sol:Borrower \
  verification/harness/DummyERC20B.sol \
  --verify flashLoanHarness:verification/spec/flashLoanAdditivity.spec \
  --link flashLoanHarness:_protocolFeesCollector=ProtocolFeesCollector \
  --solc solc7.6 \
  --cache balancerAdditivity \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-b=3,-t=1200 \
  --rule flashLoanAdditivity \
  --staging --msg "r flashLoanAdditivity with -t=1200"
    # -b must be >= 3 to pass sanity 