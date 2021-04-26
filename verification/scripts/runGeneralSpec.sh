certoraRun verification/harness/simplifiedVaultHarness.sol contracts/vault/ProtocolFeesCollector.sol verification/harness/DummyERC20.sol \
  verification/harness/FlashLoanReceiver.sol:Borrower verification/harness/WETH.sol \
  --verify simplifiedVaultHarness:verification/spec/general_spec.spec \
  --link simplifiedVaultHarness:_protocolFeesCollector=ProtocolFeesCollector \
  --link simplifiedVaultHarness:_weth=WETH \
  --solc solc7.6 \
  --cache balancerGeneral \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-copyLoopUnroll=2,-b=2,-t=1200 \
  --rule minimal_swap_info_pool_positive_total_if_registered \
  --staging --msg "general spec r minimal_swap_info_pool_positive_total_if_registered"