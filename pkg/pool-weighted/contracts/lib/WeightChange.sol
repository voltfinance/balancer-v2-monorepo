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

library WeightChange {
    using FixedPoint for uint256;

    enum WeightChangeMode { NONE, LINEAR_WEIGHT_CHANGE }

    function getNormalizedWeight(
        WeightChangeMode mode,
        uint256 startWeight,
        uint256 endWeight,
        uint256 startTime,
        uint256 endTime
    ) internal view returns (uint256) {
        uint256 pctProgress = _calculateWeightChangeProgress(startTime, endTime);
        if (mode == WeightChangeMode.NONE) {
            if (pctProgress == 0) {
                return startWeight;
            } else {
                return endWeight;
            }
        } else if (mode == WeightChangeMode.LINEAR_WEIGHT_CHANGE) {
            return _interpolateWeight(startWeight, endWeight, pctProgress);
        } else {
            _revert(Errors.UNHANDLED_WEIGHT_CHANGE_MODE);
        }
    }

    // Private functions

    function _interpolateWeight(
        uint256 startWeight,
        uint256 endWeight,
        uint256 pctProgress
    ) private pure returns (uint256) {
        if (pctProgress == 0 || startWeight == endWeight) return startWeight;
        if (pctProgress >= FixedPoint.ONE) return endWeight;

        if (startWeight > endWeight) {
            uint256 weightDelta = pctProgress.mulDown(startWeight - endWeight);
            return startWeight.sub(weightDelta);
        } else {
            uint256 weightDelta = pctProgress.mulDown(endWeight - startWeight);
            return startWeight.add(weightDelta);
        }
    }

    /**
     * @dev Returns a fixed-point number representing how far along the current weight change is, where 0 means the
     * change has not yet started, and FixedPoint.ONE means it has fully completed.
     */
    function _calculateWeightChangeProgress(uint256 startTime, uint256 endTime) private view returns (uint256) {
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
