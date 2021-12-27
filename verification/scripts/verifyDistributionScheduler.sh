certoraRun verification/harnesses/MultiDistributorHarness.sol verification/harnesses/SchedulerHarness.sol \
  --verify SchedulerHarness:verification/specs/scheduler.spec \
  --solc solc7.6 \
  --staging \
  --optimistic_loop \
  --rule oneStateAtATime \
  --rule_sanity \
  --packages @balancer-labs/v2-solidity-utils=pkg/solidity-utils @balancer-labs/v2-vault=pkg/vault \
  --msg "$1"