pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "../../contracts/vault/Authorization.sol";
import "../../contracts/vault/FlashLoanProvider.sol";
import "./internalBalanceHarness.sol";

/*
function flashLoan(
        IFlashLoanReceiver receiver,
        IERC20[] memory tokens,
        uint256[] memory amounts,
        bytes calldata receiverData
    ) external override nonReentrant {
*/

contract flashLoanHarness is internalBalanceHarness{
    constructor(IAuthorizer authorizer) internalBalanceHarness(authorizer) {}

    bytes b;

    function Harness_singleFlashLoan(IFlashLoanReceiver receiver, IERC20 token, uint256 amount) public {
        IERC20[] memory token_array = new IERC20[](1);
        token_array[0] = token;
        uint256[] memory amount_array = new uint256[](1);
        amount_array[0] = amount;
        flashLoan(receiver, token_array, amount_array, b);
    }

    function Harness_doubleFlashLoan(IFlashLoanReceiver receiver,
        IERC20 token1,
        IERC20 token2,
        uint256 amount1,
        uint256 amount2) public {

        IERC20[] memory token_array = new IERC20[](2);
        token_array[0] = token1;
        token_array[1] = token2;

        uint256[] memory amount_array = new uint256[](2);
        amount_array[0] = amount1;
        amount_array[1] = amount2;

        flashLoan(receiver, token_array, amount_array, b);
    }

    function getTokenBalance(address user, IERC20 token) public view returns (uint256) {
        return token.balanceOf(user);
    }
}