certoraRun verification/munged/distributors/contracts/RewardsScheduler.sol \
  --verify RewardsScheduler:verification/specs/sanity.spec \
  --solc solc7.6 \
  --settings -t=300 \
  --staging \
   --packages @balancer-labs/v2-solidity-utils=pkg/solidity-utils \
  --msg "SchedulerHarness sanity"