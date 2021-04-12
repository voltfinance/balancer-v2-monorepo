// SPDX-License-Identifier: agpl-3.0
pragma solidity ^0.7.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract Borrower {

    mapping (uint256 => uint256) payments;
    address vault;
    function receiveFlashLoan(
        IERC20[] calldata tokens,
        uint256[] calldata amounts,
        uint256[] calldata fees,
        bytes calldata data
    ) external {
        uint256 len = tokens.length;
        for (uint256 i = 0; i < len; i++) {
            uint256 payment = payments[i];
            require (payment <= amounts[i] + fees[i]); // Rational borrower will not donate money to the vault
            tokens[i].transfer(vault, payment);
        }
    }

}
