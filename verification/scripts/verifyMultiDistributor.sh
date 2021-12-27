certoraRun verification/harnesses/SymbolicVault.sol verification/harnesses/MultiDistributorHarness.sol \
  verification/harnesses/SymbolicERC20A.sol verification/harnesses/SymbolicERC20B.sol \
  --verify MultiDistributorHarness:verification/specs/multiDistributor.spec \
  --solc solc7.6 \
  --cloud \
  --optimistic_loop \
  --settings -t=600\
  --packages @balancer-labs/v2-solidity-utils=pkg/solidity-utils @balancer-labs/v2-vault=pkg/vault \
  --msg "$1"
  # --settings -postProcessCounterExamples=true \
  