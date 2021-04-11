certoraRun spec/harness/flashLoanHarness.sol spec/FlashLoanReceiver.sol:Borrower spec/DummyERC20.sol spec/DummyERC20B.sol \
  --verify flashLoanHarness:spec/flashLoanAdditivity.spec \
  --solc solc7.6 \
  --cache balancerAdditivity \
  --settings -ignoreViewFunctions,-assumeUnwindCond,-b=3 \
  --staging --msg "flash loan additivity"
    # -b must be >= 3 to pass sanity 