certoraRun verification/harness/simplifiedVaultHarness.sol \
  --verify simplifiedVaultHarness:verification/spec/sanity.spec \
  --solc solc7.6 \
  --settings -t=300,-recursionEntryLimit=6 \
  --cache balancer_sanity \
  --msg "Simplified Vault sanity"
