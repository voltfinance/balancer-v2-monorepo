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

import "./BaseWeightedPool.sol";

/**
 * @dev Weighted Pool with mutable weights, designed to support V2 Liquidity Bootstrapping
 */
abstract contract FixedTokenWeightedPool is BaseWeightedPool {
    // State variables

    uint256 internal immutable _totalTokens;

    IERC20 internal immutable _token0;
    IERC20 internal immutable _token1;
    IERC20 internal immutable _token2;
    IERC20 internal immutable _token3;

    // All token balances are normalized to behave as if the token had 18 decimals. We assume a token's decimals will
    // not change throughout its lifetime, and store the corresponding scaling factor for each at construction time.
    // These factors are always greater than or equal to one: tokens with more than 18 decimals are not supported.

    uint256 internal immutable _scalingFactor0;
    uint256 internal immutable _scalingFactor1;
    uint256 internal immutable _scalingFactor2;
    uint256 internal immutable _scalingFactor3;

    constructor(
        IVault vault,
        string memory name,
        string memory symbol,
        IERC20[] memory tokens,
        address[] memory assetManagers,
        uint256 swapFeePercentage,
        uint256 pauseWindowDuration,
        uint256 bufferPeriodDuration,
        address owner
    )
        BaseWeightedPool(
            vault,
            name,
            symbol,
            tokens,
            assetManagers,
            swapFeePercentage,
            pauseWindowDuration,
            bufferPeriodDuration,
            owner
        )
    {
        uint256 totalTokens = tokens.length;
        _totalTokens = totalTokens;

        // Immutable variables cannot be initialized inside an if statement, so we must do conditional assignments
        _token0 = totalTokens > 0 ? tokens[0] : IERC20(0);
        _token1 = totalTokens > 1 ? tokens[1] : IERC20(0);
        _token2 = totalTokens > 2 ? tokens[2] : IERC20(0);
        _token3 = totalTokens > 3 ? tokens[3] : IERC20(0);

        _scalingFactor0 = totalTokens > 0 ? _computeScalingFactor(tokens[0]) : 0;
        _scalingFactor1 = totalTokens > 1 ? _computeScalingFactor(tokens[1]) : 0;
        _scalingFactor2 = totalTokens > 2 ? _computeScalingFactor(tokens[2]) : 0;
        _scalingFactor3 = totalTokens > 3 ? _computeScalingFactor(tokens[3]) : 0;
    }

    function _getTotalTokens() internal view virtual override returns (uint256) {
        return _totalTokens;
    }

    function _getTokenIndex(IERC20 token) internal view virtual override returns (uint256) {
        // prettier-ignore
        {
            if (token == _token0) { return 0; }
            else if (token == _token1) { return 1; }
            else if (token == _token2) { return 2; }
            else if (token == _token3) { return 3; }
            else {
                _revert(Errors.INVALID_TOKEN);
            }
        }
    }

    function _scalingFactor(IERC20 token) internal view virtual override returns (uint256) {
        // prettier-ignore
        if (token == _token0) { return _scalingFactor0; }
        else if (token == _token1) { return _scalingFactor1; }
        else if (token == _token2) { return _scalingFactor2; }
        else if (token == _token3) { return _scalingFactor3; }
        else {
            _revert(Errors.INVALID_TOKEN);
        }
    }

    function _scalingFactors() internal view virtual override returns (uint256[] memory) {
        uint256 totalTokens = _getTotalTokens();
        uint256[] memory scalingFactors = new uint256[](totalTokens);

        // prettier-ignore
        {
            if (totalTokens > 0) { scalingFactors[0] = _scalingFactor0; } else { return scalingFactors; }
            if (totalTokens > 1) { scalingFactors[1] = _scalingFactor1; } else { return scalingFactors; }
            if (totalTokens > 2) { scalingFactors[2] = _scalingFactor2; } else { return scalingFactors; }
            if (totalTokens > 3) { scalingFactors[3] = _scalingFactor3; } else { return scalingFactors; }
        }

        return scalingFactors;
    }
}
