cp contracts/vault/balances/SimpleBalanceAllocation.sol contracts/vault/balances/BalanceAllocation.sol
certoraRun spec/harness/solvencyHarness.sol spec/DummyERC20.sol spec/DummyERC20B.sol spec/FlashLoanReceiver.sol:Borrower \
  --verify solvencyHarness:spec/solvency.spec \
  --solc solc7.6 \
  --cache balancerSolvency \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-copyLoopUnroll=2,-b=2,-nonIterEdgeBlocksRemoval \
  --rule vault_never_changes_total_supply \
  --staging --msg "vault_never_changes_total_supply with swaps and nonIterEdgeBlocksRemoval"
cp contracts/vault/balances/BalanceAllocation.orig contracts/vault/balances/BalanceAllocation.sol