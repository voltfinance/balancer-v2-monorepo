certoraRun contracts/vault/Vault.sol \
  --verify Vault:verification/spec/sanity.spec \
  --solc solc7.6 \
  --settings -t=300,-recursionEntryLimit=6 \
  --cache balancer_sanity \
  --staging --msg "Vault sanity with unsafe transfers"
