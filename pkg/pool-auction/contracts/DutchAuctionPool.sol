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
import "@balancer-labs/v2-solidity-utils/contracts/helpers/ERC20Helpers.sol";
import "@balancer-labs/v2-solidity-utils/contracts/helpers/InputHelpers.sol";

import "@balancer-labs/v2-vault/contracts/interfaces/IMinimalSwapInfoPool.sol";
import "@balancer-labs/v2-pool-utils/contracts/BasePool.sol";

import "./AuctionPoolUserDataHelpers.sol";
import "./DutchAuctionPoolMiscData.sol";

// solhint-disable not-rely-on-time

/**
 * @dev Base class for WeightedPools containing swap, join and exit logic, but leaving storage and management of
 * the weights to subclasses. Derived contracts can choose to make weights immutable, mutable, or even dynamic
 *  based on local or external logic.
 */
contract DutchAuctionPool is IMinimalSwapInfoPool, BasePool {
    using FixedPoint for uint256;
    using DutchAuctionPoolMiscData for bytes32;
    using AuctionPoolUserDataHelpers for bytes;

    uint256 private constant _TOTAL_TOKENS = 3;

    bytes32 internal _miscData;

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
        BasePool(
            vault,
            IVault.PoolSpecialization.MINIMAL_SWAP_INFO,
            name,
            symbol,
            _sortTokens(paymentToken, commitmentToken, ticketToken),
            new address[](_TOTAL_TOKENS),
            1e12, // Swap fees aren't charged but BasePool requires a non-zero value so give minimum
            pauseWindowDuration,
            bufferPeriodDuration,
            owner
        )
    {
        // Set tokens
        _paymentToken = paymentToken;
        _commitmentToken = commitmentToken;
        _ticketToken = ticketToken;

        // Set token indexes
        (_paymentTokenIndex, _commitmentTokenIndex, _ticketTokenIndex) = _getSortedTokenIndexes(
            paymentToken,
            commitmentToken,
            ticketToken
        );

        IERC20[] memory tokens = _sortTokens(paymentToken, commitmentToken, ticketToken);
        _scalingFactor0 = _computeScalingFactor(tokens[0]);
        _scalingFactor1 = _computeScalingFactor(tokens[1]);
        _scalingFactor2 = _computeScalingFactor(tokens[2]);
    }

    // Getters / Setters

    function _getTotalTokens() internal pure override returns (uint256) {
        return _TOTAL_TOKENS;
    }

    function _getMaxTokens() internal pure override returns (uint256) {
        return _TOTAL_TOKENS;
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

    // Auction-specific Getters

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
        (, uint256[] memory balances, ) = getVault().getPoolTokens(getPoolId());
        _upscaleArray(balances, _scalingFactors());

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
        // Equivalent to tokenPrice >= clearingPrice
        // but prevents double calculation of tokenPrice
        return getTokenPrice() >= getAuctionPrice();
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
        uint256 scalingFactorTokenIn = _scalingFactor(request.tokenIn);
        uint256 scalingFactorTokenOut = _scalingFactor(request.tokenOut);
        request.amount = _upscale(
            request.amount,
            request.kind == IVault.SwapKind.GIVEN_IN ? scalingFactorTokenIn : scalingFactorTokenOut
        );

        // The quoted amount out for GIVEN_IN swaps and vice versa
        uint256 quoteAmount;

        if (getAuctionSuccessful()) {
            // Check if Auction has sold all tokens
            quoteAmount = _onClaimTicketTokens(request);
        } else if (getAuctionEnded()) {
            // Check if Auction has finished unsuccessfully
            quoteAmount = _onRefundCommitmentTokens(request);
        } else {
            // Otherwise attempt to commit tokens
            quoteAmount = _onCommitPaymentTokens(request);
        }

        if (request.kind == IVault.SwapKind.GIVEN_IN) {
            // quoteAmount tokens are exiting the Pool, so we round down.
            return _downscaleDown(quoteAmount, scalingFactorTokenOut);
        } else {
            // quoteAmount tokens are entering the Pool, so we round up.
            return _downscaleUp(quoteAmount, scalingFactorTokenIn);
        }
    }

    function _onClaimTicketTokens(SwapRequest memory swapRequest) internal view virtual returns (uint256) {
        // Claiming ticketTokens for commitmentTokens
        require(
            swapRequest.tokenIn == _commitmentToken && swapRequest.tokenOut == _ticketToken,
            "Must claim ticketTokens"
        );

        // The exchange rate for claiming ticketTokens
        // is defined by the auctions clearing price.
        // Note: As the auction is successful tokenPrice == clearingPrice
        if (swapRequest.kind == IVault.SwapKind.GIVEN_IN) {
            return swapRequest.amount.divDown(getTokenPrice());
        } else {
            return swapRequest.amount.mulDown(getTokenPrice());
        }
    }

    function _onRefundCommitmentTokens(SwapRequest memory swapRequest) internal view virtual returns (uint256) {
        // Auction failed and now we can only refund commitmentTokens for paymentTokens.
        require(
            swapRequest.tokenIn == _commitmentToken && swapRequest.tokenOut == _paymentToken,
            "Must refund commitmentTokens into paymentTokens"
        );

        // Refunding committed tokens is a 1:1 process
        return swapRequest.amount;
    }

    function _onCommitPaymentTokens(SwapRequest memory swapRequest)
        internal
        view
        virtual
        whenNotPaused
        returns (uint256)
    {
        // Committing tokens is disabled while the contract is paused.

        require(_miscData.startTime() < block.timestamp, "Auction hasn't started yet");
        // Auction is in progress and we only allow trading paymentToken for commitmentToken
        require(
            swapRequest.tokenIn == _paymentToken && swapRequest.tokenOut == _commitmentToken,
            "Must commit paymentTokens for commitmentTokens"
        );

        // Committing tokens is a 1:1 process
        return swapRequest.amount;
    }

    // Join Hook

    function _onInitializePool(
        bytes32,
        address,
        address,
        uint256[] memory scalingFactors,
        bytes memory userData
    ) internal override returns (uint256 bptAmountOut, uint256[] memory amountsIn) {
        amountsIn = userData.initialAmountsIn();
        require(amountsIn[_paymentTokenIndex] == 0, "Can't provide payment token liquidity");
        require(
            amountsIn[_commitmentTokenIndex] > 0 && amountsIn[_ticketTokenIndex] > 0,
            "Must provide commitment and ticketTokens"
        );

        // Mint 1 BPT for each token being added
        bptAmountOut = amountsIn[_ticketTokenIndex];

        // TODO: Add real data here
        // TODO: Move to a separate function?
        bytes32 auctionData;

        uint256 startTime = 100;
        require(startTime > block.timestamp, "startTime has already passed");
        auctionData = auctionData.setStartTime(startTime);

        uint256 endTime = 1000;
        require(endTime > startTime, "endTime must be after startTime");
        auctionData = auctionData.setEndTime(endTime);

        // We can calculate the start price from the implied price from if all commitmentTokens are bought
        uint256 scaledCommitmentBalance = _upscale(
            amountsIn[_commitmentTokenIndex],
            scalingFactors[_commitmentTokenIndex]
        );
        uint256 scaledTicketBalance = _upscale(amountsIn[_ticketTokenIndex], scalingFactors[_ticketTokenIndex]);
        uint256 startPrice = scaledCommitmentBalance.divUp(scaledTicketBalance);
        auctionData = auctionData.setStartPrice(startPrice);

        uint256 minimumPrice = 0;
        require(minimumPrice <= startPrice, "Minimum price must be less than or equal to start price");
        auctionData = auctionData.setMinimumPrice(minimumPrice);
        _miscData = auctionData;

        return (bptAmountOut, amountsIn);
    }

    function _onJoinPool(
        bytes32,
        address,
        address,
        uint256[] memory,
        uint256,
        uint256,
        uint256[] memory,
        bytes memory
    )
        internal
        pure
        override
        returns (
            uint256,
            uint256[] memory,
            uint256[] memory
        )
    {
        // We disallow any liquidity provision after initialization.
        revert("Already initialized");
    }

    // Exit Hook

    function _onExitPool(
        bytes32,
        address,
        address,
        uint256[] memory balances,
        uint256,
        uint256,
        uint256[] memory,
        bytes memory userData
    )
        internal
        view
        override
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

    // Scaling

    /**
     * @dev Returns the scaling factor for one of the Pool's tokens.
     */
    function _scalingFactor(uint256 index) internal view returns (uint256) {
        if (index == 0) return _scalingFactor0;
        if (index == 1) return _scalingFactor1;
        return _scalingFactor2;
    }

    /**
     * @dev Returns the scaling factor for one of the Pool's tokens.
     */
    function _scalingFactor(IERC20 token) internal view override returns (uint256) {
        if (token == _paymentToken) return _scalingFactor(_paymentTokenIndex);
        if (token == _commitmentToken) return _scalingFactor(_commitmentTokenIndex);
        return _scalingFactor(_ticketTokenIndex);
    }

    /**
     * @dev Same as `_scalingFactor()`, except for all registered tokens (in the same order as registered). The Vault
     * will always pass balances in this order when calling any of the Pool hooks.
     */
    function _scalingFactors() internal view override returns (uint256[] memory) {
        uint256[] memory scalingFactors = new uint256[](_TOTAL_TOKENS);

        scalingFactors[0] = _scalingFactor0;
        scalingFactors[1] = _scalingFactor1;
        scalingFactors[2] = _scalingFactor2;

        return scalingFactors;
    }
}
