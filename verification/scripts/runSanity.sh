certoraRun contracts/vault/Vault.sol \
  --verify Vault:verification/spec/sanity.spec \
  --solc solc7.6 \
  --settings -t=300 \
  --debug \
  --staging --msg "Vault sanity"
