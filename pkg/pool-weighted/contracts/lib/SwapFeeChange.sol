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

import "@balancer-labs/v2-solidity-utils/contracts/math/FixedPoint.sol";

pragma solidity ^0.7.0;

library SwapFeeChange {
    using FixedPoint for uint256;

    enum SwapFeeChangeMode { NONE, LINEAR_SWAP_FEE_CHANGE }

    function getSwapFeePercentage(
        SwapFeeChangeMode mode,
        uint256 startSwapFeePercentage,
        uint256 endSwapFeePercentage,
        uint256 startTime,
        uint256 endTime
    ) internal view returns (uint256) {
        if (mode == SwapFeeChangeMode.NONE) {
            return endSwapFeePercentage;
        } else if (mode == SwapFeeChangeMode.LINEAR_SWAP_FEE_CHANGE) {
            uint256 pctProgress = _calculateSwapFeeChangeProgress(startTime, endTime);
            return _interpolateSwapFeePercentage(startSwapFeePercentage, endSwapFeePercentage, pctProgress);
        } else {
            _revert(Errors.UNHANDLED_SWAP_FEE_CHANGE_MODE);
        }
    }

    // Private functions

    function _interpolateSwapFeePercentage(
        uint256 startSwapFeePercentage,
        uint256 endSwapFeePercentage,
        uint256 pctProgress
    ) private pure returns (uint256) {
        if (pctProgress == 0 || startSwapFeePercentage == endSwapFeePercentage) return startSwapFeePercentage;
        if (pctProgress >= FixedPoint.ONE) return endSwapFeePercentage;

        if (startSwapFeePercentage > endSwapFeePercentage) {
            uint256 swapFeePercentageDeltta = pctProgress.mulDown(startSwapFeePercentage - endSwapFeePercentage);
            return startSwapFeePercentage.sub(swapFeePercentageDeltta);
        } else {
            uint256 swapFeePercentageDeltta = pctProgress.mulDown(endSwapFeePercentage - startSwapFeePercentage);
            return startSwapFeePercentage.add(swapFeePercentageDeltta);
        }
    }

    /**
     * @dev Returns a fixed-point number representing how far along the current swap fee percentage change is, where 0
     * means the change has not yet started, and FixedPoint.ONE means it has fully completed.
     */
    function _calculateSwapFeeChangeProgress(uint256 startTime, uint256 endTime) private view returns (uint256) {
        uint256 currentTime = block.timestamp;

        if (currentTime > endTime) {
            return FixedPoint.ONE;
        } else if (currentTime < startTime) {
            return 0;
        }

        // No need for SafeMath as it was checked right above: endTime >= currentTime >= startTime
        uint256 totalSeconds = endTime - startTime;
        uint256 secondsElapsed = currentTime - startTime;

        // In the degenerate case of a zero duration change, consider it completed (and avoid division by zero)
        return totalSeconds == 0 ? FixedPoint.ONE : secondsElapsed.divDown(totalSeconds);
    }
}
