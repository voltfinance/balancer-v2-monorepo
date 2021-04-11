certoraRun spec/harness/ethHarness.sol spec/DummyERC20.sol spec/DummyERC20B.sol spec/FlashLoanReceiver.sol:Borrower \
  --verify ethHarness:spec/eth.spec \
  --solc solc7.6 \
  --cache balancerEth \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-copyLoopUnroll=2,-nonIterEdgeBlocksRemoval,-b=0 \
  --method 'changeRelayerAllowance(address,bool)' \
  --rule vault_gets_no_eth \
  --staging --msg "running eth with zero loop iterations"