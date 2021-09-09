// SPDX-License-Identifier: GPL-3.0-or-later
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "@balancer-labs/v2-solidity-utils/contracts/math/FixedPoint.sol";
import "@balancer-labs/v2-solidity-utils/contracts/helpers/InputHelpers.sol";

import "@balancer-labs/v2-pool-utils/contracts/BaseMinimalSwapInfoPool.sol";

import "./AuctionPoolUserDataHelpers.sol";
import "./DutchAuctionPoolMiscData.sol";

// solhint-disable not-rely-on-time

/**
 * @dev Base class for WeightedPools containing swap, join and exit logic, but leaving storage and management of
 * the weights to subclasses. Derived contracts can choose to make weights immutable, mutable, or even dynamic
 *  based on local or external logic.
 */
abstract contract DutchAuctionPool is
    IMinimalSwapInfoPool,
    BasePoolAuthorization,
    BalancerPoolToken,
    TemporarilyPausable
{
    using FixedPoint for uint256;
    using DutchAuctionPoolMiscData for bytes32;
    using AuctionPoolUserDataHelpers for bytes;

    bytes32 internal _miscData;

    IVault private immutable _vault;
    bytes32 private immutable _poolId;

    uint256 internal immutable _paymentTokenIndex;
    uint256 internal immutable _commitmentTokenIndex;
    uint256 internal immutable _ticketTokenIndex;

    IERC20 internal immutable _paymentToken;
    IERC20 internal immutable _commitmentToken;
    IERC20 internal immutable _ticketToken;

    // All token balances are normalized to behave as if the token had 18 decimals. We assume a token's decimals will
    // not change throughout its lifetime, and store the corresponding scaling factor for each at construction time.
    // These factors are always greater than or equal to one: tokens with more than 18 decimals are not supported.
    uint256 internal immutable _scalingFactor0;
    uint256 internal immutable _scalingFactor1;
    uint256 internal immutable _scalingFactor2;

    uint256 internal _finalTicketPrice;

    modifier onlyVault(bytes32 poolId) {
        _require(msg.sender == address(getVault()), Errors.CALLER_NOT_VAULT);
        _require(poolId == getPoolId(), Errors.INVALID_POOL_ID);
        _;
    }

    constructor(
        IVault vault,
        string memory name,
        string memory symbol,
        IERC20 paymentToken,
        IERC20 commitmentToken,
        IERC20 ticketToken,
        uint256 pauseWindowDuration,
        uint256 bufferPeriodDuration,
        address owner
    )
        // Base Pools are expected to be deployed using factories. By using the factory address as the action
        // disambiguator, we make all Pools deployed by the same factory share action identifiers. This allows for
        // simpler management of permissions (such as being able to manage granting the 'set fee percentage' action in
        // any Pool created by the same factory), while still making action identifiers unique among different factories
        // if the selectors match, preventing accidental errors.
        Authentication(bytes32(uint256(msg.sender)))
        BalancerPoolToken(name, symbol)
        BasePoolAuthorization(owner)
        TemporarilyPausable(pauseWindowDuration, bufferPeriodDuration)
    {
        bytes32 poolId = vault.registerPool(IVault.PoolSpecialization.MINIMAL_SWAP_INFO);

        uint256 paymentTokenIndex;
        uint256 commitmentTokenIndex;
        uint256 ticketTokenIndex;
        if (ticketToken < commitmentToken && ticketToken < paymentToken) {
            commitmentTokenIndex = commitmentToken < paymentToken ? 1 : 2;
            paymentTokenIndex = paymentToken < commitmentToken ? 1 : 2;
            // ticketTokenIndex = 0;
        } else if (paymentToken < commitmentToken && paymentToken < ticketToken) {
            // paymentTokenIndex = 0;
            commitmentTokenIndex = commitmentToken < ticketToken ? 1 : 2;
            ticketTokenIndex = ticketToken < commitmentToken ? 1 : 2;
        } else {
            paymentTokenIndex = paymentToken < ticketToken ? 1 : 2;
            // commitmentTokenIndex = 0;
            ticketTokenIndex = ticketToken < paymentToken ? 1 : 2;
        }

        IERC20[] memory tokens = new IERC20[](3);
        tokens[paymentTokenIndex] = paymentToken;
        tokens[commitmentTokenIndex] = commitmentToken;
        tokens[ticketTokenIndex] = ticketToken;

        // Pass in zero addresses for Asset Managers
        vault.registerTokens(poolId, tokens, new address[](3));

        // Set immutable state variables - these cannot be read from during construction
        _vault = vault;
        _poolId = poolId;

        _paymentToken = paymentToken;
        _commitmentToken = commitmentToken;
        _ticketToken = ticketToken;

        _paymentTokenIndex = paymentTokenIndex;
        _commitmentTokenIndex = commitmentTokenIndex;
        _ticketTokenIndex = ticketTokenIndex;

        _scalingFactor0 = _computeScalingFactor(tokens[0]);
        _scalingFactor1 = _computeScalingFactor(tokens[1]);
        _scalingFactor2 = _computeScalingFactor(tokens[2]);
    }

    // Getters / Setters

    function getVault() public view returns (IVault) {
        return _vault;
    }

    function getPoolId() public view override returns (bytes32) {
        return _poolId;
    }

    function getMiscData()
        public
        view
        returns (
            uint256 startTime,
            uint256 endTime,
            uint256 startPrice,
            uint256 minimumPrice
        )
    {
        bytes32 miscData = _miscData;
        startTime = miscData.startTime();
        endTime = miscData.endTime();
        startPrice = miscData.startPrice();
        minimumPrice = miscData.minimumPrice();
    }

    function getAuctionPrice() public view returns (uint256) {
        (uint256 startTime, uint256 endTime, uint256 startPrice, uint256 minimumPrice) = getMiscData();
        if (block.timestamp <= startTime) {
            return startPrice;
        }

        if (block.timestamp >= endTime) {
            return minimumPrice;
        }

        uint256 totalSeconds = endTime - startTime;
        uint256 secondsElapsed = block.timestamp - startTime;
        uint256 weightDelta = secondsElapsed.divDown(totalSeconds).mulDown(startPrice - minimumPrice);
        return startPrice.sub(weightDelta);
    }

    function getTokenPrice() public view returns (uint256) {
        if (_finalTicketPrice != 0) return _finalTicketPrice;
        (, uint256[] memory balances, ) = getVault().getPoolTokens(getPoolId());

        // TODO: properly scale this for decimals
        return balances[_paymentTokenIndex].mulDown(balances[_ticketTokenIndex]);
    }

    /**
     * @notice The current clearing price of the Dutch auction.
     * @return The bigger from tokenPrice and auctionPrice.
     */
    function getClearingPrice() public view returns (uint256) {
        uint256 tokenPrice = getTokenPrice();
        uint256 auctionPrice = getAuctionPrice();

        return tokenPrice > auctionPrice ? tokenPrice : auctionPrice;
    }

    /**
     * @notice Successful if tokens sold equals totalTokens.
     * @return True if tokenPrice is bigger or equal clearingPrice.
     */
    function getAuctionSuccessful() public view returns (bool) {
        return getTokenPrice() >= getClearingPrice();
    }

    /**
     * @notice Checks if the auction has ended.
     * @return True if auction is successful or time has ended.
     */
    function getAuctionEnded() public view returns (bool) {
        return getAuctionSuccessful() || block.timestamp > _miscData.endTime();
    }

    // Swap hooks

    function onSwap(
        SwapRequest memory request,
        uint256,
        uint256
    ) public virtual override onlyVault(request.poolId) returns (uint256) {
        // Check if Auction has sold all tokens
        if (getAuctionSuccessful()) {
            return _onClaimTicketTokens(request);
        }

        // Check if Auction has finished unsuccessfully
        if (getAuctionEnded()) {
            return _onRefundCommitmentTokens(request);
        }

        return _onCommitPaymentTokens(request);
    }

    function _onClaimTicketTokens(SwapRequest memory swapRequest) internal view virtual returns (uint256) {
        uint256 scalingFactorTokenIn = _scalingFactor(swapRequest.tokenIn);
        uint256 scalingFactorTokenOut = _scalingFactor(swapRequest.tokenOut);

        // TODO: EIP2929 probably makes this worse than just recalculating. Check this.
        uint256 finalTicketPrice = _finalTicketPrice;
        if (finalTicketPrice == 0) {
            finalTicketPrice = getTokenPrice();
        }

        // Claiming ticketTokens for commitmentTokens
        require(
            swapRequest.tokenIn == _commitmentToken && swapRequest.tokenOut == _ticketToken,
            "Must claim ticketTokens"
        );
        if (swapRequest.kind == IVault.SwapKind.GIVEN_IN) {
            swapRequest.amount = _upscale(swapRequest.amount, scalingFactorTokenIn);

            // TODO: properly scale finalTicketPrice for token decimals
            uint256 amountOut = swapRequest.amount.divDown(finalTicketPrice);

            // amountOut tokens are exiting the Pool, so we round down.
            return _downscaleDown(amountOut, scalingFactorTokenOut);
        } else {
            swapRequest.amount = _upscale(swapRequest.amount, scalingFactorTokenOut);

            // TODO: properly scale finalTicketPrice for token decimals
            uint256 amountIn = swapRequest.amount.mulDown(finalTicketPrice);

            // amountIn tokens are entering the Pool, so we round up.
            return _downscaleUp(amountIn, scalingFactorTokenIn);
        }
    }

    function _onRefundCommitmentTokens(SwapRequest memory swapRequest) internal view virtual returns (uint256) {
        uint256 scalingFactorTokenIn = _scalingFactor(swapRequest.tokenIn);
        uint256 scalingFactorTokenOut = _scalingFactor(swapRequest.tokenOut);

        // Auction failed and now we can only refund commitmentTokens for paymentTokens.
        require(
            swapRequest.tokenIn == _commitmentToken && swapRequest.tokenOut == _paymentToken,
            "Must refund commitmentTokens into paymentTokens"
        );

        if (swapRequest.kind == IVault.SwapKind.GIVEN_IN) {
            uint256 amountOut = _upscale(swapRequest.amount, scalingFactorTokenIn);

            // amountOut tokens are exiting the Pool, so we round down.
            return _downscaleDown(amountOut, scalingFactorTokenOut);
        } else {
            uint256 amountIn = _upscale(swapRequest.amount, scalingFactorTokenOut);

            // amountIn tokens are entering the Pool, so we round up.
            return _downscaleUp(amountIn, scalingFactorTokenIn);
        }
    }

    function _onCommitPaymentTokens(SwapRequest memory swapRequest)
        internal
        view
        virtual
        whenNotPaused
        returns (uint256)
    {
        // Committing tokens is disabled while the contract is paused.
        uint256 scalingFactorTokenIn = _scalingFactor(swapRequest.tokenIn);
        uint256 scalingFactorTokenOut = _scalingFactor(swapRequest.tokenOut);

        require(_miscData.startTime() < block.timestamp, "Auction hasn't started yet");
        // Auction is in progress and we only allow trading paymentToken for commitmentToken
        require(
            swapRequest.tokenIn == _paymentToken && swapRequest.tokenOut == _commitmentToken,
            "Must commit paymentTokens for commitmentTokens"
        );

        if (swapRequest.kind == IVault.SwapKind.GIVEN_IN) {
            uint256 amountOut = _upscale(swapRequest.amount, scalingFactorTokenIn);

            // amountOut tokens are exiting the Pool, so we round down.
            return _downscaleDown(amountOut, scalingFactorTokenOut);
        } else {
            uint256 amountIn = _upscale(swapRequest.amount, scalingFactorTokenOut);

            // amountIn tokens are entering the Pool, so we round up.
            return _downscaleUp(amountIn, scalingFactorTokenIn);
        }
    }

    // Join Hook

    function onJoinPool(
        bytes32 poolId,
        address sender,
        address recipient,
        uint256[] memory balances,
        uint256 lastChangeBlock,
        uint256 protocolSwapFeePercentage,
        bytes memory userData
    ) public virtual override onlyVault(poolId) whenNotPaused returns (uint256[] memory, uint256[] memory) {
        // It would be strange for the Pool to be paused before it is initialized, but for consistency we prevent
        // initialization in this case.

        // We disallow any liquidity provision after initialization.
        require(totalSupply() == 0, "Already initialized");

        require(sender == getOwner(), "Only owner may initialize pool");

        (uint256 bptAmountOut, uint256[] memory amountsIn, uint256[] memory dueProtocolFeeAmounts) = _onJoinPool(
            poolId,
            sender,
            recipient,
            balances,
            lastChangeBlock,
            protocolSwapFeePercentage,
            userData
        );

        _mintPoolTokens(recipient, bptAmountOut);
        return (amountsIn, dueProtocolFeeAmounts);
    }

    function _onJoinPool(
        bytes32,
        address,
        address,
        uint256[] memory,
        uint256,
        uint256,
        bytes memory userData
    )
        private
        returns (
            uint256 bptAmountOut,
            uint256[] memory amountsIn,
            uint256[] memory dueProtocolFeeAmounts
        )
    {
        amountsIn = userData.initialAmountsIn();
        require(amountsIn[_paymentTokenIndex] == 0, "Can't provide payment token liquidity");
        require(
            amountsIn[_commitmentTokenIndex] > 0 && amountsIn[_ticketTokenIndex] > 0,
            "Must provider commitment and ticketTokens"
        );

        // Mint 1 BPT for each token being added
        bptAmountOut = amountsIn[_ticketTokenIndex];

        // TODO: Add real data here
        bytes32 auctionData;

        uint256 startTime = 100;
        require(startTime > block.timestamp, "startTime has already passed");
        auctionData = auctionData.setStartTime(startTime);

        uint256 endTime = 1000;
        require(endTime > startTime, "endTime must be after startTime");
        auctionData = auctionData.setEndTime(endTime);

        // We can calculate the start price from the implied price from if all commitmentTokens are bought
        uint256 startPrice = amountsIn[_commitmentTokenIndex].divUp(amountsIn[_ticketTokenIndex]);
        auctionData = auctionData.setStartPrice(startPrice);

        uint256 minimumPrice = 0;
        require(minimumPrice <= startPrice, "Minimum price must be less than or equal to start price");
        auctionData = auctionData.setMinimumPrice(minimumPrice);
        _miscData = auctionData;


        // There are no due protocol fee amounts during initialization
        dueProtocolFeeAmounts = new uint256[](3);
        return (bptAmountOut, amountsIn, dueProtocolFeeAmounts);
    }

    // Exit Hook

    function onExitPool(
        bytes32 poolId,
        address sender,
        address recipient,
        uint256[] memory balances,
        uint256 lastChangeBlock,
        uint256 protocolSwapFeePercentage,
        bytes memory userData
    ) public virtual override onlyVault(poolId) returns (uint256[] memory, uint256[] memory) {
        _upscaleArray(balances);

        (uint256 bptAmountIn, uint256[] memory amountsOut, uint256[] memory dueProtocolFeeAmounts) = _onExitPool(
            poolId,
            sender,
            recipient,
            balances,
            lastChangeBlock,
            protocolSwapFeePercentage,
            userData
        );

        // Note we no longer use `balances` after calling `_onExitPool`, which may mutate it.

        _burnPoolTokens(sender, bptAmountIn);

        // Both amountsOut and dueProtocolFeeAmounts are amounts exiting the Pool, so we round down.
        _downscaleDownArray(amountsOut);
        _downscaleDownArray(dueProtocolFeeAmounts);

        return (amountsOut, dueProtocolFeeAmounts);
    }

    function _onExitPool(
        bytes32,
        address,
        address,
        uint256[] memory balances,
        uint256,
        uint256,
        bytes memory userData
    )
        internal
        virtual
        returns (
            uint256 bptAmountIn,
            uint256[] memory amountsOut,
            uint256[] memory dueProtocolFeeAmounts
        )
    {
        // Note that there is no minimum amountOut parameter: this is handled by `IVault.exitPool`.
        require(getAuctionEnded(), "Can't exit until auction has completed");

        bptAmountIn = userData.exactBptInForTokensOut();
        if (getAuctionSuccessful()) {
            // If auction was successful, owner can withdraw paymentTokens
            amountsOut[_paymentTokenIndex] = Math.divDown(
                Math.mul(balances[_paymentTokenIndex], bptAmountIn),
                totalSupply()
            );
        } else {
            // If auction was unsuccessful, owner can withdraw ticketTokens
            amountsOut[_ticketTokenIndex] = Math.divDown(
                Math.mul(balances[_ticketTokenIndex], bptAmountIn),
                totalSupply()
            );
        }

        return (bptAmountIn, amountsOut, dueProtocolFeeAmounts);
    }

    // Query functions

    /**
     * @dev Returns the amount of BPT that would be granted to `recipient` if the `onJoinPool` hook were called by the
     * Vault with the same arguments, along with the number of tokens `sender` would have to supply.
     *
     * This function is not meant to be called directly, but rather from a helper contract that fetches current Vault
     * data, such as the protocol swap fee percentage and Pool balances.
     *
     * Like `IVault.queryBatchSwap`, this function is not view due to internal implementation details: the caller must
     * explicitly use eth_call instead of eth_sendTransaction.
     */
    function queryJoin(
        bytes32 poolId,
        address sender,
        address recipient,
        uint256[] memory balances,
        uint256 lastChangeBlock,
        uint256 protocolSwapFeePercentage,
        bytes memory userData
    ) external returns (uint256 bptOut, uint256[] memory amountsIn) {
        InputHelpers.ensureInputLengthMatch(balances.length, 3);

        _queryAction(
            poolId,
            sender,
            recipient,
            balances,
            lastChangeBlock,
            protocolSwapFeePercentage,
            userData,
            _onJoinPool,
            _downscaleUpArray
        );

        // The `return` opcode is executed directly inside `_queryAction`, so execution never reaches this statement,
        // and we don't need to return anything here - it just silences compiler warnings.
        return (bptOut, amountsIn);
    }

    /**
     * @dev Returns the amount of BPT that would be burned from `sender` if the `onExitPool` hook were called by the
     * Vault with the same arguments, along with the number of tokens `recipient` would receive.
     *
     * This function is not meant to be called directly, but rather from a helper contract that fetches current Vault
     * data, such as the protocol swap fee percentage and Pool balances.
     *
     * Like `IVault.queryBatchSwap`, this function is not view due to internal implementation details: the caller must
     * explicitly use eth_call instead of eth_sendTransaction.
     */
    function queryExit(
        bytes32 poolId,
        address sender,
        address recipient,
        uint256[] memory balances,
        uint256 lastChangeBlock,
        uint256 protocolSwapFeePercentage,
        bytes memory userData
    ) external returns (uint256 bptIn, uint256[] memory amountsOut) {
        InputHelpers.ensureInputLengthMatch(balances.length, 3);

        _queryAction(
            poolId,
            sender,
            recipient,
            balances,
            lastChangeBlock,
            protocolSwapFeePercentage,
            userData,
            _onExitPool,
            _downscaleDownArray
        );

        // The `return` opcode is executed directly inside `_queryAction`, so execution never reaches this statement,
        // and we don't need to return anything here - it just silences compiler warnings.
        return (bptIn, amountsOut);
    }

    // Scaling

    /**
     * @dev Returns a scaling factor that, when multiplied to a token amount for `token`, normalizes its balance as if
     * it had 18 decimals.
     */
    function _computeScalingFactor(IERC20 token) private view returns (uint256) {
        // Tokens that don't implement the `decimals` method are not supported.
        uint256 tokenDecimals = ERC20(address(token)).decimals();

        // Tokens with more than 18 decimals are not supported.
        uint256 decimalsDifference = Math.sub(18, tokenDecimals);
        return 10**decimalsDifference;
    }

    /**
     * @dev Returns the scaling factor for one of the Pool's tokens. Reverts if `token` is not a token registered by the
     * Pool.
     */
    function _scalingFactor(uint256 index) internal view returns (uint256) {
        if (index == 0) return _scalingFactor0;
        if (index == 1) return _scalingFactor1;
        return _scalingFactor2;
    }

    /**
     * @dev Returns the scaling factor for one of the Pool's tokens. Reverts if `token` is not a token registered by the
     * Pool.
     */
    function _scalingFactor(IERC20 token) internal view returns (uint256) {
        if (token == _paymentToken) return _scalingFactor(_paymentTokenIndex);
        if (token == _commitmentToken) return _scalingFactor(_commitmentTokenIndex);
        return _scalingFactor(_ticketTokenIndex);
    }

    /**
     * @dev Applies `scalingFactor` to `amount`, resulting in a larger or equal value depending on whether it needed
     * scaling or not.
     */
    function _upscale(uint256 amount, uint256 scalingFactor) internal pure returns (uint256) {
        return Math.mul(amount, scalingFactor);
    }

    /**
     * @dev Same as `_upscale`, but for an entire array (of two elements). This function does not return anything, but
     * instead *mutates* the `amounts` array.
     */
    function _upscaleArray(uint256[] memory amounts) internal view {
        amounts[0] = Math.mul(amounts[0], _scalingFactor0);
        amounts[1] = Math.mul(amounts[1], _scalingFactor1);
        amounts[2] = Math.mul(amounts[2], _scalingFactor2);
    }

    /**
     * @dev Reverses the `scalingFactor` applied to `amount`, resulting in a smaller or equal value depending on
     * whether it needed scaling or not. The result is rounded down.
     */
    function _downscaleDown(uint256 amount, uint256 scalingFactor) internal pure returns (uint256) {
        return Math.divDown(amount, scalingFactor);
    }

    /**
     * @dev Same as `_downscaleDown`, but for an entire array (of two elements). This function does not return anything,
     * but instead *mutates* the `amounts` array.
     */
    function _downscaleDownArray(uint256[] memory amounts) internal view {
        amounts[0] = Math.divDown(amounts[0], _scalingFactor0);
        amounts[1] = Math.divDown(amounts[1], _scalingFactor1);
        amounts[2] = Math.divDown(amounts[2], _scalingFactor2);
    }

    /**
     * @dev Reverses the `scalingFactor` applied to `amount`, resulting in a smaller or equal value depending on
     * whether it needed scaling or not. The result is rounded up.
     */
    function _downscaleUp(uint256 amount, uint256 scalingFactor) internal pure returns (uint256) {
        return Math.divUp(amount, scalingFactor);
    }

    /**
     * @dev Same as `_downscaleUp`, but for an entire array (of two elements). This function does not return anything,
     * but instead *mutates* the `amounts` array.
     */
    function _downscaleUpArray(uint256[] memory amounts) internal view {
        amounts[0] = Math.divUp(amounts[0], _scalingFactor0);
        amounts[1] = Math.divUp(amounts[1], _scalingFactor1);
        amounts[2] = Math.divUp(amounts[2], _scalingFactor2);
    }

    function _getAuthorizer() internal view override returns (IAuthorizer) {
        // Access control management is delegated to the Vault's Authorizer. This lets Balancer Governance manage which
        // accounts can call permissioned functions: for example, to perform emergency pauses.
        // If the owner is delegated, then *all* permissioned functions, including `setSwapFeePercentage`, will be under
        // Governance control.
        return getVault().getAuthorizer();
    }

    function _queryAction(
        bytes32 poolId,
        address sender,
        address recipient,
        uint256[] memory balances,
        uint256 lastChangeBlock,
        uint256 protocolSwapFeePercentage,
        bytes memory userData,
        function(bytes32, address, address, uint256[] memory, uint256, uint256, bytes memory)
            internal
            returns (uint256, uint256[] memory, uint256[] memory) _action,
        function(uint256[] memory) internal view _downscaleArray
    ) private {
        // This uses the same technique used by the Vault in queryBatchSwap. Refer to that function for a detailed
        // explanation.

        if (msg.sender != address(this)) {
            // We perform an external call to ourselves, forwarding the same calldata. In this call, the else clause of
            // the preceding if statement will be executed instead.

            // solhint-disable-next-line avoid-low-level-calls
            (bool success, ) = address(this).call(msg.data);

            // solhint-disable-next-line no-inline-assembly
            assembly {
                // This call should always revert to decode the bpt and token amounts from the revert reason
                switch success
                    case 0 {
                        // Note we are manually writing the memory slot 0. We can safely overwrite whatever is
                        // stored there as we take full control of the execution and then immediately return.

                        // We copy the first 4 bytes to check if it matches with the expected signature, otherwise
                        // there was another revert reason and we should forward it.
                        returndatacopy(0, 0, 0x04)
                        let error := and(mload(0), 0xffffffff00000000000000000000000000000000000000000000000000000000)

                        // If the first 4 bytes don't match with the expected signature, we forward the revert reason.
                        if eq(eq(error, 0x43adbafb00000000000000000000000000000000000000000000000000000000), 0) {
                            returndatacopy(0, 0, returndatasize())
                            revert(0, returndatasize())
                        }

                        // The returndata contains the signature, followed by the raw memory representation of the
                        // `bptAmount` and `tokenAmounts` (array: length + data). We need to return an ABI-encoded
                        // representation of these.
                        // An ABI-encoded response will include one additional field to indicate the starting offset of
                        // the `tokenAmounts` array. The `bptAmount` will be laid out in the first word of the
                        // returndata.
                        //
                        // In returndata:
                        // [ signature ][ bptAmount ][ tokenAmounts length ][ tokenAmounts values ]
                        // [  4 bytes  ][  32 bytes ][       32 bytes      ][ (32 * length) bytes ]
                        //
                        // We now need to return (ABI-encoded values):
                        // [ bptAmount ][ tokeAmounts offset ][ tokenAmounts length ][ tokenAmounts values ]
                        // [  32 bytes ][       32 bytes     ][       32 bytes      ][ (32 * length) bytes ]

                        // We copy 32 bytes for the `bptAmount` from returndata into memory.
                        // Note that we skip the first 4 bytes for the error signature
                        returndatacopy(0, 0x04, 32)

                        // The offsets are 32-bytes long, so the array of `tokenAmounts` will start after
                        // the initial 64 bytes.
                        mstore(0x20, 64)

                        // We now copy the raw memory array for the `tokenAmounts` from returndata into memory.
                        // Since bpt amount and offset take up 64 bytes, we start copying at address 0x40. We also
                        // skip the first 36 bytes from returndata, which correspond to the signature plus bpt amount.
                        returndatacopy(0x40, 0x24, sub(returndatasize(), 36))

                        // We finally return the ABI-encoded uint256 and the array, which has a total length equal to
                        // the size of returndata, plus the 32 bytes of the offset but without the 4 bytes of the
                        // error signature.
                        return(0, add(returndatasize(), 28))
                    }
                    default {
                        // This call should always revert, but we fail nonetheless if that didn't happen
                        invalid()
                    }
            }
        } else {
            _upscaleArray(balances);

            (uint256 bptAmount, uint256[] memory tokenAmounts, ) = _action(
                poolId,
                sender,
                recipient,
                balances,
                lastChangeBlock,
                protocolSwapFeePercentage,
                userData
            );

            _downscaleArray(tokenAmounts);

            // solhint-disable-next-line no-inline-assembly
            assembly {
                // We will return a raw representation of `bptAmount` and `tokenAmounts` in memory, which is composed of
                // a 32-byte uint256, followed by a 32-byte for the array length, and finally the 32-byte uint256 values
                // Because revert expects a size in bytes, we multiply the array length (stored at `tokenAmounts`) by 32
                let size := mul(mload(tokenAmounts), 32)

                // We store the `bptAmount` in the previous slot to the `tokenAmounts` array. We can make sure there
                // will be at least one available slot due to how the memory scratch space works.
                // We can safely overwrite whatever is stored in this slot as we will revert immediately after that.
                let start := sub(tokenAmounts, 0x20)
                mstore(start, bptAmount)

                // We send one extra value for the error signature "QueryError(uint256,uint256[])" which is 0x43adbafb
                // We use the previous slot to `bptAmount`.
                mstore(sub(start, 0x20), 0x0000000000000000000000000000000000000000000000000000000043adbafb)
                start := sub(start, 0x04)

                // When copying from `tokenAmounts` into returndata, we copy the additional 68 bytes to also return
                // the `bptAmount`, the array length, and the error signature.
                revert(start, add(size, 68))
            }
        }
    }
}
