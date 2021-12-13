certoraRun verification/harnesses/SymbolicVault.sol verification/harnesses/MultiDistributorHarness.sol \
  verification/harnesses/SymbolicERC20A.sol verification/harnesses/SymbolicERC20B.sol \
  --verify MultiDistributorHarness:verification/specs/multiDistributor.spec \
  --solc solc7.6 \
  --staging \
  --optimistic_loop \
  --rule userSubStakeCorrelationWithTotalSupply \
  --packages @balancer-labs/v2-solidity-utils=pkg/solidity-utils @balancer-labs/v2-vault=pkg/vault \
  --msg "$1"