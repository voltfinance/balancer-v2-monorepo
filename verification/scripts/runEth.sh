certoraRun verification/harness/ethHarness.sol verification/harness/DummyERC20.sol verification/harness/DummyERC20B.sol verification/harness/FlashLoanReceiver.sol:Borrower verification/harness/WETH.sol  \
  --verify ethHarness:verification/spec/eth.spec \
  --solc solc7.6 \
  --cache balancerEth \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-copyLoopUnroll=2,-nonIterEdgeBlocksRemoval,-b=2 \
  --rule receive_asset_called_at_most_once_per_token \
  --staging shelly/optimizerWeeklyTesting --msg "running eth -r receive_asset_called_at_most_once_per_token with two loop iterations"
