certoraRun verification/harness/tokenOrderHarness.sol contracts/vault/ProtocolFeesCollector.sol verification/harness/DummyERC20.sol \
  verification/harness/FlashLoanReceiver.sol:Borrower verification/harness/WETH.sol \
  --verify tokenOrderHarness:verification/spec/tokenOrder.spec \
  --link tokenOrderHarness:_protocolFeesCollector=ProtocolFeesCollector \
  --link tokenOrderHarness:_weth=WETH \
  --solc solc7.6 \
  --cache balancerTokenOrder \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-copyLoopUnroll=2,-b=2 \
  --staging --msg "runTokenOrder all rules"