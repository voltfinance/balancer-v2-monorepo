certoraRun verification/harnesses/MultiDistributorHarness.sol \
  --verify MultiDistributorHarness:verification/specs/sanity.spec \
  --solc solc7.6 \
  --settings -t=300 \
  --staging \
  --optimistic_loop \
  --packages @balancer-labs/v2-solidity-utils=pkg/solidity-utils @balancer-labs/v2-vault=pkg/vault \
  --msg "MultiDistrHarness sanity"