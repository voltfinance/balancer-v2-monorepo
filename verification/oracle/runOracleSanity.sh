certoraRun contracts/pools/weighted/WeightedPool2Tokens.sol \
  --verify WeightedPool2Tokens:verification/spec/sanity.spec \
  --solc solc7.6 \
  --settings -t=300,-recursionEntryLimit=6 \
  --cache balancer_oracle_sanity \
  --staging --msg "Oracle pool sanity"
