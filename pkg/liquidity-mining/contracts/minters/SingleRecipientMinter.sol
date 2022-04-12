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

import "@balancer-labs/v2-solidity-utils/contracts/math/FixedPoint.sol";
import "@balancer-labs/v2-solidity-utils/contracts/openzeppelin/IERC20.sol";
import "@balancer-labs/v2-solidity-utils/contracts/openzeppelin/ReentrancyGuard.sol";

import "../interfaces/IBalancerTokenAdmin.sol";

abstract contract SingleRecipientMinter is ReentrancyGuard {
    using FixedPoint for uint256;

    IERC20 internal immutable _balToken;
    IBalancerTokenAdmin private immutable _tokenAdmin;

    address private _recipient;

    uint256 private _rate;
    uint256 private _lastMintTimestamp;
    uint256 private _previousFutureEpochTime;

    uint256 private constant _BAL_INFLATION_FRACTION = 1e17; // 10% of total BAL inflation

    constructor(IBalancerTokenAdmin tokenAdmin, address recipient, uint256 startTime) {
        IERC20 balToken = tokenAdmin.getBalancerToken();

        _balToken = balToken;
        _tokenAdmin = tokenAdmin;

        _recipient = recipient;

        require(startTime >= block.timestamp, "Can only start minting in the future");

        _rate = tokenAdmin.rate().mulDown(_BAL_INFLATION_FRACTION);
        _lastMintTimestamp = _roundUpTimestamp(startTime);
        _previousFutureEpochTime = tokenAdmin.futureEpochTimeWrite();
    }

    /**
     * @notice Returns the address of the Balancer Governance Token
     */
    function getBalancerToken() external view returns (IERC20) {
        return _balToken;
    }

    /**
     * @notice Returns the address of the Balancer Token Admin contract
     */
    function getBalancerTokenAdmin() external view returns (IBalancerTokenAdmin) {
        return _tokenAdmin;
    }

    function mint() external nonReentrant returns (uint256) {
        uint256 lastMintTimestamp = _lastMintTimestamp;
        if (lastMintTimestamp == block.timestamp) return 0;

        uint256 previousFutureEpochTime = _previousFutureEpochTime;

        uint256 mintAmount;
        if (block.timestamp >= previousFutureEpochTime){
            // We've crossed an epoch boundary in the BAL inflation schedule so we must account for this.
            // We assume that we'll only cross a single epoch boundary as crossing multiple would require
            // nobody to call mint on this contract for over a year.

            uint256 newRate = _tokenAdmin.rate().mulDown(_BAL_INFLATION_FRACTION);

            // Calculate how much is to be minted using the old inflation rate
            uint256 durationInCurrentEpoch = previousFutureEpochTime - lastMintTimestamp;
            mintAmount = _rate * durationInCurrentEpoch;
            
            // Calculate how much is to be minted using the new inflation rate
            uint256 durationInNewEpoch = block.timestamp - previousFutureEpochTime;
            mintAmount += newRate * durationInNewEpoch;
            
            _rate = newRate;
            _previousFutureEpochTime = _tokenAdmin.futureEpochTimeWrite();
        } else {
            // The entire period to be minted falls in the same epoch so we can simply use the cached rate.

            uint256 durationToMint = block.timestamp - _lastMintTimestamp;
            mintAmount = _rate * durationToMint;
        }

        _lastMintTimestamp = block.timestamp;
        _tokenAdmin.mint(_recipient, mintAmount);

        return mintAmount;
    }

    /**
     * @dev Rounds the provided timestamp down to the beginning of the previous week (Thurs 00:00 UTC)
     */
    function _roundDownTimestamp(uint256 timestamp) private pure returns (uint256) {
        return (timestamp / 1 weeks) * 1 weeks;
    }

    /**
     * @dev Rounds the provided timestamp up to the beginning of the next week (Thurs 00:00 UTC)
     */
    function _roundUpTimestamp(uint256 timestamp) private pure returns (uint256) {
        return _roundDownTimestamp(timestamp + 1 weeks - 1);
    }
}
