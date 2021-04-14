# Private to internal
perl -0777 -i -pe 's/uint256 private constant/uint256 internal constant/g' contracts/vault/ProtocolFeesCollector.sol
perl -0777 -i -pe 's/private/internal/g' contracts/vault/PoolRegistry.sol

# External to public
perl -0777 -i -pe 's/external/public/g' contracts/vault/UserBalance.sol
perl -0777 -i -pe 's/external/public/g' contracts/vault/FlashLoanProvider.sol

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

# simplifying BallanceAllocation
perl -007 -i -pe 's/uint256 mask = 2\*\*\(224\) - 1;//g' contracts/vault/balances/BalanceAllocation.sol
perl -007 -i -pe 's/uint256 mask = 2\*\*\(32\) - 1;//g' contracts/vault/balances/BalanceAllocation.sol
perl -007 -i -pe 's/uint256 mask = 2\*\*\(112\) - 1;//g' contracts/vault/balances/BalanceAllocation.sol
perl -007 -i -pe 's/uint256 mask = 2\*\*\(112\) - 1;//g' contracts/vault/balances/BalanceAllocation.sol

perl -007 -i -pe 's/return \(uint256\(balance\) & mask\) == 0/return uint256\(balance\) == 0/g' contracts/vault/balances/BalanceAllocation.sol
perl -007 -i -pe 's/return uint256\(balance >> 224\) & mask/return 0/g' contracts/vault/balances/BalanceAllocation.sol
perl -007 -i -pe 's/return uint256\(balance >> 112\) & mask/return 0/g' contracts/vault/balances/BalanceAllocation.sol
perl -007 -i -pe 's/return uint256\(balance\) & mask/return uint256\(balance\)/g' contracts/vault/balances/BalanceAllocation.sol
perl -007 -i -pe 's/\(\(\_mostSignificant << 224\) \+ \(\_midSignificant << 112\) \+ \_leastSignificant\)/\(\_leastSignificant\)/g' contracts/vault/balances/BalanceAllocation.sol


perl -007 -i -pe 's/& mask//g' contracts/vault/balances/BalanceAllocation.sol
