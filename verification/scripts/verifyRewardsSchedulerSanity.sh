certoraRun verification/munged/distributors/contracts/DistributionScheduler.sol \
  --verify DistributionScheduler:verification/specs/sanity.spec \
  --solc solc7.6 \
  --settings -t=300 \
  --staging alex/fix-expdataflowanalysis-sources \
  --packages @balancer-labs/v2-solidity-utils=pkg/solidity-utils \
  --msg "SchedulerHarness sanity"