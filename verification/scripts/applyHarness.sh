# Private to internal
perl -0777 -i -pe 's/uint256 private constant/uint256 internal constant/g' contracts/vault/ProtocolFeesCollector.sol
perl -0777 -i -pe 's/private/internal/g' contracts/vault/PoolRegistry.sol

# Virtualize
perl -0777 -i -pe 's/_calculateFlashLoanFee\(uint256 amount\) internal/_calculateFlashLoanFee\(uint256 amount\) virtual internal/g' contracts/vault/Fees.sol
perl -0777 -i -pe 's/function \_authenticateCaller\(\) internal/function \_authenticateCaller\(\) virtual internal/g' contracts/lib/helpers/Authentication.sol
perl -0777 -i -pe 's/\_getPoolSpecialization\(bytes32 poolId\) internal pure/\_getPoolSpecialization\(bytes32 poolId\) virtual internal view/g' contracts/vault/PoolRegistry.sol
perl -0777 -i -pe 's/function \_validateSignature\(address user, uint256 errorCode\) internal {/function \_validateSignature\(address user, uint256 errorCode\) internal virtual {/g' contracts/lib/helpers/SignaturesValidator.sol

# sendValue => nothing inteface
perl -0007 -i -pe 's/recipient\.sendValue\(amount\)/Nothing\(recipient\)\.nop{value:amount}\(\)/g' contracts/vault/AssetTransfersHandler.sol
perl -0007 -i -pe 's/msg\.sender\.sendValue\(excess\)/Nothing\(msg\.sender\)\.nop{value:excess}\(\)/g' contracts/vault/AssetTransfersHandler.sol
perl -0007 -i -pe 's/;\s*abstract contract/;
interface Nothing { function nop\(\) external payable; }
abstract contract/g' contracts/vault/AssetTransfersHandler.sol

# remove problematic modifiers
perl -0007 -i -pe 's/nonReentrant //g' contracts/vault/Swaps.sol
perl -0007 -i -pe 's/noEmergencyPeriod //g' contracts/vault/Swaps.sol
