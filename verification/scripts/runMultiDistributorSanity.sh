certoraRun verification/munged/distributors/contracts/MultiDistributor.sol \
  --verify MultiDistributor:verification/specs/sanity.spec \
  --solc solc7.6 \
  --settings -t=300 \
  --staging \
  --packages @balancer-labs/v2-solidity-utils=pkg/solidity-utils @balancer-labs/v2-vault=pkg/vault \
  --msg "SchedulerHarness sanity"