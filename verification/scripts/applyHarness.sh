# Private to internal
perl -0777 -i -pe 's/uint256 private constant/uint256 internal constant/g' contracts/vault/ProtocolFeesCollector.sol
perl -0777 -i -pe 's/private/internal/g' contracts/vault/PoolRegistry.sol

# Virtualize
perl -0777 -i -pe 's/_calculateFlashLoanFee\(uint256 amount\) internal/_calculateFlashLoanFee\(uint256 amount\) virtual internal/g' contracts/vault/Fees.sol
perl -0777 -i -pe 's/function \_authenticateCaller\(\) internal/function \_authenticateCaller\(\) virtual internal/g' contracts/lib/helpers/Authentication.sol
perl -0777 -i -pe 's/\_getPoolSpecialization\(bytes32 poolId\) internal pure/\_getPoolSpecialization\(bytes32 poolId\) virtual internal view/g' contracts/vault/PoolRegistry.sol