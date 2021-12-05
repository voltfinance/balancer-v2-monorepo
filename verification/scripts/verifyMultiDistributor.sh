certoraRun verification/harnesses/MultiDistributorHarness.sol \
  --verify MultiDistributorHarness:verification/specs/multiDistributor.spec \
  --solc solc7.6 \
  --settings -t=300 \
  --cloud \
  --optimistic_loop \
  --packages @balancer-labs/v2-solidity-utils=pkg/solidity-utils @balancer-labs/v2-vault=pkg/vault \
  --rule globalGreaterOrEqualUser \
  --msg "$1"