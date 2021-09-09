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

import "@balancer-labs/v2-solidity-utils/contracts/helpers/WordCodec.sol";

/**
 * @dev This module provides an interface to store seemingly unrelated pieces of information, in particular used by
 * pools with a price oracle.
 *
 * These pieces of information are all kept together in a single storage slot to reduce the number of storage reads. In
 * particular, we not only store configuration values (such as the swap fee percentage), but also cache
 * reduced-precision versions of the total BPT supply and invariant, which lets us not access nor compute these values
 * when producing oracle updates during a swap.
 *
 * Data is stored with the following structure:
 *
 * [ swap fee pct | oracle enabled | oracle index | oracle sample initial timestamp |  end time  |  start time   ]
 * [    uint64    |      bool      |    uint10    |              uint31             |   uint32   |    uint32     ]
 *
 * Note that we are not using the most-significant 106 bits.
 */
library DutchAuctionPoolMiscData {
    using WordCodec for bytes32;
    using WordCodec for uint256;

    // TODO: Settle on an actual storage layout here. Values are leftover from oracle pools
    uint256 private constant _START_TIME_OFFSET = 0;
    uint256 private constant _END_TIME_OFFSET = 32;
    uint256 private constant _START_PRICE_OFFSET = 44;
    uint256 private constant _MIN_PRICE_OFFSET = 75;

    /**
     * @dev Returns the cached logarithm of the invariant.
     */
    function startTime(bytes32 data) internal pure returns (uint256) {
        return data.decodeUint32(_START_TIME_OFFSET);
    }

    /**
     * @dev Returns the cached logarithm of the total supply.
     */
    function endTime(bytes32 data) internal pure returns (uint256) {
        return data.decodeUint32(_END_TIME_OFFSET);
    }

    /**
     * @dev Returns the timestamp of the creation of the oracle's latest sample.
     */
    function startPrice(bytes32 data) internal pure returns (uint256) {
        return data.decodeUint31(_START_PRICE_OFFSET);
    }

    /**
     * @dev Returns the index of the oracle's latest sample.
     */
    function minimumPrice(bytes32 data) internal pure returns (uint256) {
        return data.decodeUint10(_MIN_PRICE_OFFSET);
    }

    /**
     * @dev Sets the logarithm of the total supply in `data`, returning the updated value.
     */
    function setStartTime(bytes32 data, uint256 _startTime) internal pure returns (bytes32) {
        return data.insertUint31(_startTime, _START_TIME_OFFSET);
    }

    /**
     * @dev Sets the timestamp of the creation of the oracle's latest sample in `data`, returning the updated value.
     */
    function setEndTime(bytes32 data, uint256 _endTime) internal pure returns (bytes32) {
        return data.insertUint31(_endTime, _END_TIME_OFFSET);
    }

    /**
     * @dev Sets the index of the  oracle's latest sample in `data`, returning the updated value.
     */
    function setStartPrice(bytes32 data, uint256 _startPrice) internal pure returns (bytes32) {
        return data.insertUint10(_startPrice, _START_PRICE_OFFSET);
    }

    /**
     * @dev Enables or disables the oracle in `data`, returning the updated value.
     */
    function setMinimumPrice(bytes32 data, uint256 _minimumPrice) internal pure returns (bytes32) {
        return data.insertUint10(_minimumPrice, _MIN_PRICE_OFFSET);
    }
}
