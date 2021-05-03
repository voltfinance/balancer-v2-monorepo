certoraRun verification/oracle/WeightedPool2TokensHarness.sol \
  --verify WeightedPool2TokensHarness:verification/oracle/updateOracleRevert.spec \
  --solc solc7.6 \
  --settings -t=300,-recursionEntryLimit=6,-ruleSanityChecks,-assumeUnwindCond,-b=3 \
  --cache balancer_oracle_revert \
  --staging shelly/forBalancer \
  --msg "Oracle pool - updateOracle should not revert, Shelly's branch"
