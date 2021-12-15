certoraRun verification/harnesses/MultiDistributorHarness.sol verification/harnesses/SchedulerHarness.sol \
  --verify SchedulerHarness:verification/specs/scheduler.spec \
  --solc solc7.6 \
  --staging Eyal/CVLAndStorageType \
  --optimistic_loop \
  --rule scheduleExistInitializedParams \
  --packages @balancer-labs/v2-solidity-utils=pkg/solidity-utils @balancer-labs/v2-vault=pkg/vault \
  --msg "$1"


  #   verification/harnesses/SymbolicERC20A.sol verification/harnesses/SymbolicERC20B.sol \