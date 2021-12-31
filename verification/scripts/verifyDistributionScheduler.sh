certoraRun verification/harnesses/MultiDistributorHarness.sol verification/harnesses/SchedulerHarness.sol \
    verification/harnesses/SymbolicERC20A.sol verification/harnesses/SymbolicERC20B.sol \
  --verify SchedulerHarness:verification/specs/scheduler.spec \
  --solc solc7.6 \
  --staging \
  --rule transition_DistScheduleCreated_To_DistStarted \
  --rule_sanity \
  --optimistic_loop \
  --packages @balancer-labs/v2-solidity-utils=pkg/solidity-utils @balancer-labs/v2-vault=pkg/vault \
  --msg "$1"