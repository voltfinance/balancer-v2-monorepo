// SPDX-License-Identifier: MIT


pragma solidity ^0.7.0;

/* solhint-disable */

/**
 * This file is an oversimplified, WRONG implementation of LogExpMath used for verification.
 * We do NOT care about the mathematical soundness, so we do not mind what the return values are.
 */
library SmartFakeLogExpMath {
    // All fixed point multiplications and divisions are inlined. This means we need to divide by ONE when multiplying
    // two numbers, and multiply by ONE when dividing them.

    // All arguments and return values are 18 decimal fixed point numbers.
    int256 constant ONE_18 = 1e18;

    // Internally, intermediate values are computed with higher precision as 20 decimal fixed point numbers, and in the
    // case of ln36, 36 decimals.
    int256 constant ONE_20 = 1e20;
    int256 constant ONE_36 = 1e36;


    /**
     * @dev Exponentiation (x^y) with unsigned 18 decimal fixed point base and exponent.
     *
     * Reverts if ln(x) * y is smaller than `MIN_NATURAL_EXPONENT`, or larger than `MAX_NATURAL_EXPONENT`.
     */
    function pow(uint256 x, uint256 y) internal pure returns (uint256) {
        if (y == 0) {
            // We solve the 0^0 indetermination by making it equal one.
            return uint256(ONE_18);
        }

        if (x == 0) {
            return 0;
        }

        if (x == uint256(ONE_18)) {
            return uint256(ONE_18);
        }

        // // The ln function takes a signed value, so we need to make sure x fits in the signed 256 bit range.
        if (x >= 2 ** 255) return 2 ** 255 - 1; 

        if (y == uint256(ONE_18)) {
            return x;
        }

        if (y < uint256(ONE_18)) {
            return x-1 > 0 ? x-1 : 1; 
        } else {
            // y > ONE_18
            return x + 1 > 0 ? x : x+1; 
        }
    }

    /**
     * @dev Natural exponentiation (e^x) with signed 18 decimal fixed point exponent.
     *
     * Reverts if `x` is smaller than MIN_NATURAL_EXPONENT, or larger than `MAX_NATURAL_EXPONENT`.
     */
    function exp(int256 x) internal pure returns (int256) {
       if (x == 0) {
           return ONE_18;
       }
    //    require (x+1 > 0);
       if (x+1 == 0) return x;
       return ONE_18 + 1 > x + 1 ? ONE_18 + 1 : x + 1;
    }

    /**
     * @dev Logarithm (log(arg, base), with signed 18 decimal fixed point base and argument.
     */
    function log(int256 arg, int256 base) internal pure returns (int256) {
        if (arg == ONE_18) return 0;
        if (arg > ONE_18) {
            return 1;
        } else {
            return -1;
        }
    }

    /**
     * @dev Natural logarithm (ln(a)) with signed 18 decimal fixed point argument.
     */
    function ln(int256 a) internal pure returns (int256) {
        return _ln(a);
    }

    /**
     * @dev Internal natural logarithm (ln(a)) with signed 18 decimal fixed point argument.
     */
    function _ln(int256 a) private pure returns (int256) {
        if (a == ONE_18) return 0;
        if (a > ONE_18) {
            return 1;
        } else {
            return -1;
        }
    }

    /**
     * @dev Intrnal high precision (36 decimal places) natural logarithm (ln(x)) with signed 18 decimal fixed point argument,
     * for x close to one.
     *
     * Should only be used if x is between LN_36_LOWER_BOUND and LN_36_UPPER_BOUND.
     */
    function _ln_36(int256 x) private pure returns (int256) {
        return _ln(x);
    }
}
