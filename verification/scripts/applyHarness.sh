# Private to internal
perl -0777 -i -pe 's/uint256 private constant/uint256 internal constant/g' contracts/vault/ProtocolFeesCollector.sol
perl -0777 -i -pe 's/private/internal/g' contracts/vault/PoolRegistry.sol

# External to public
perl -0777 -i -pe 's/external/public/g' contracts/vault/UserBalance.sol
perl -0777 -i -pe 's/external/public/g' contracts/vault/FlashLoans.sol
perl -0777 -i -pe 's/external/public/g' contracts/vault/PoolBalances.sol
perl -0777 -i -pe 's/external/public/g' contracts/vault/ProtocolFeesCollector.sol

# Virtualize
perl -0777 -i -pe 's/_calculateFlashLoanFee\(uint256 amount\) internal/_calculateFlashLoanFee\(uint256 amount\) virtual internal/g' contracts/vault/Fees.sol
perl -0777 -i -pe 's/function \_authenticateCaller\(\) internal/function \_authenticateCaller\(\) virtual internal/g' contracts/lib/helpers/Authentication.sol
perl -0777 -i -pe 's/\_getPoolSpecialization\(bytes32 poolId\) internal pure/\_getPoolSpecialization\(bytes32 poolId\) virtual internal view/g' contracts/vault/PoolRegistry.sol
perl -0777 -i -pe 's/function \_validateSignature\(address user, uint256 errorCode\) internal {/function \_validateSignature\(address user, uint256 errorCode\) internal virtual {/g' contracts/lib/helpers/SignaturesValidator.sol
perl -0777 -i -pe 's/\_calculateFlashLoanFeeAmount\(uint256 amount\) internal view/\_calculateFlashLoanFeeAmount\(uint256 amount\) internal virtual view/g' contracts/vault/Fees.sol

# sendValue => nothing inteface
perl -0777 -i -pe 's/recipient\.sendValue\(amount\)/Nothing\(recipient\)\.nop{value:amount}\(\)/g' contracts/vault/AssetTransfersHandler.sol
perl -0777 -i -pe 's/msg\.sender\.sendValue\(excess\)/Nothing\(msg\.sender\)\.nop{value:excess}\(\)/g' contracts/vault/AssetTransfersHandler.sol
perl -0777 -i -pe 's/;\s*abstract contract/;
interface Nothing { function nop\(\) external payable; }
abstract contract/g' contracts/vault/AssetTransfersHandler.sol

# remove problematic modifiers
perl -0777 -i -pe 's/nonReentrant //g' contracts/vault/Swaps.sol
perl -0777 -i -pe 's/whenNotPaused //g' contracts/vault/Swaps.sol
perl -0777 -i -pe 's/nonReentrant //g' contracts/vault/PoolBalances.sol
perl -0777 -i -pe 's/whenNotPaused //g' contracts/vault/PoolBalances.sol
perl -0777 -i -pe 's/nonReentrant //g' contracts/vault/FlashLoans.sol
perl -0777 -i -pe 's/whenNotPaused //g' contracts/vault/FlashLoans.sol
perl -0777 -i -pe 's/, ReentrancyGuard//g' contracts/vault/FlashLoans.sol
perl -0777 -i -pe 's/, TemporarilyPausable //g' contracts/vault/FlashLoans.sol

# simplifying BallanceAllocation
perl -0777 -i -pe 's/uint256 mask = 2\*\*\(224\) - 1;//g' contracts/vault/balances/BalanceAllocation.sol
perl -0777 -i -pe 's/uint256 mask = 2\*\*\(32\) - 1;//g' contracts/vault/balances/BalanceAllocation.sol
perl -0777 -i -pe 's/uint256 mask = 2\*\*\(112\) - 1;//g' contracts/vault/balances/BalanceAllocation.sol
perl -0777 -i -pe 's/uint256 mask = 2\*\*\(112\) - 1;//g' contracts/vault/balances/BalanceAllocation.sol

perl -0777 -i -pe 's/return \(uint256\(balance\) & mask\) == 0/return uint256\(balance\) == 0/g' contracts/vault/balances/BalanceAllocation.sol
perl -0777 -i -pe 's/return uint256\(balance >> 224\) & mask/return 0/g' contracts/vault/balances/BalanceAllocation.sol
perl -0777 -i -pe 's/return uint256\(balance >> 112\) & mask/return 0/g' contracts/vault/balances/BalanceAllocation.sol
perl -0777 -i -pe 's/return uint256\(balance\) & mask/return uint256\(balance\)/g' contracts/vault/balances/BalanceAllocation.sol
perl -0777 -i -pe 's/\(\(\_mostSignificant << 224\) \+ \(\_midSignificant << 112\) \+ \_leastSignificant\)/\(\_leastSignificant\)/g' contracts/vault/balances/BalanceAllocation.sol

perl -0777 -i -pe 's/return \(uint256\(balance\) & mask\) == 0/return uint256\(balance\) == 0/g' contracts/vault/balances/BalanceAllocation.sol
perl -0777 -i -pe 's/return uint256\(balance >> 224\) & mask/return 0/g' contracts/vault/balances/BalanceAllocation.sol
perl -0777 -i -pe 's/return uint256\(balance >> 112\) & mask/return 0/g' contracts/vault/balances/BalanceAllocation.sol
perl -0777 -i -pe 's/return uint256\(balance\) & mask/return uint256\(balance\)/g' contracts/vault/balances/BalanceAllocation.sol
perl -0777 -i -pe 's/\(\(\_mostSignificant << 224\) \+ \(\_midSignificant << 112\) \+ \_leastSignificant\)/\(\_leastSignificant\)/g' contracts/vault/balances/BalanceAllocation.sol
perl -0777 -i -pe 's/& mask//g' contracts/vault/balances/BalanceAllocation.sol

# remove swap deadline
perl -0777 -i -pe 's/       \_require\(block.timestamp <= deadline, Errors.SWAP_DEADLINE\)/     \/\/   \_require\(block.timestamp <= deadline, Errors.SWAP_DEADLINE\)/g' contracts/vault/Swaps.sol

# joinPool and exitPool to public
perl -0777 -i -pe 's/external/public/g' contracts/vault/PoolBalances.sol

# _validateTokensAndGetBalances to internal
perl -0777 -i -pe 's/function \_validateTokensAndGetBalances\(bytes32 poolId, IERC20\[\] memory expectedTokens\)\s*private\s*view/function \_validateTokensAndGetBalances\(bytes32 poolId, IERC20\[\] memory expectedTokens\) internal view/g' contracts/vault/PoolBalances.sol

# internal to public _getInternalBalance
perl -0777 -i -pe 's/function \_getInternalBalance\(address account, IERC20 token\) internal view/function \_getInternalBalance\(address account, IERC20 token\) public view/g' contracts/vault/UserBalance.sol

# remove unneccesary inputlength check
perl -0777 -i -pe 's/InputHelpers\.ensureInputLengthMatch\(tokens\.length, amounts\.length\);//g' contracts/vault/FlashLoans.sol
perl -0777 -i -pe 's/InputHelpers\.ensureInputLengthMatch\(change\.assets\.length, change\.limits\.length\);//g' contracts/vault/PoolBalances.sol

# remove event emitting in join and exit pool
perl -0777 -i -pe 's/bool positive = kind == PoolBalanceChangeKind\.JOIN;//g' contracts/vault/PoolBalances.sol
perl -0777 -i -pe 's/emit PoolBalanceChanged\(\s*poolId,\s*sender,\s*tokens.\s*\/\/.*\s*\_unsafeCastToInt256\(amountsInOrOut, positive\),\s*paidProtocolSwapFeeAmounts\s*\);//g' contracts/vault/PoolBalances.sol

# remove event from FlashLoans
perl -0777 -i -pe 's/emit FlashLoan\(recipient, token, amounts\[i\], receivedFeeAmount\);//g' contracts/vault/FlashLoans.sol

# safeTransfers to transfers
perl -0777 -i -pe 's/safeT/t/g' contracts/vault/Fees.sol
perl -0777 -i -pe 's/safeT/t/g' contracts/vault/FlashLoans.sol
perl -0777 -i -pe 's/safeT/t/g' contracts/vault/UserBalance.sol
perl -0777 -i -pe 's/safeT/t/g' contracts/vault/AssetManagers.sol