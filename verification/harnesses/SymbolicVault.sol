pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "@balancer-labs/v2-solidity-utils/contracts/math/Math.sol";

import "@balancer-labs/v2-solidity-utils/contracts/openzeppelin/IERC20.sol";

contract SymbolicVault {
    using Math for uint256;


    //Store the balanceof from each token to account 
    mapping (address  => mapping (address => uint)) public balanceOf;

    enum UserBalanceOpKind { DEPOSIT_INTERNAL, WITHDRAW_INTERNAL, TRANSFER_INTERNAL, TRANSFER_EXTERNAL }
    
    struct UserBalanceOp {
        UserBalanceOpKind kind;
        address asset;
        uint256 amount;
        address sender;
        address payable recipient;
    }

    function manageUserBalance(UserBalanceOp[] memory ops) external payable {
    	for(uint256 i; i < ops.length ; i++) {

    		uint256 amount =  ops[i].amount;

            address recipient = ops[i].recipient;
            address sender = ops[i].sender;
            address asset = ops[i].asset;

    		if (ops[i].kind ==  UserBalanceOpKind.DEPOSIT_INTERNAL) {
    			IERC20(asset).transferFrom(sender, address(this),amount);
    			balanceOf[asset][recipient] = balanceOf[asset][recipient].add(amount);
    		}
    		else if (ops[i].kind ==  UserBalanceOpKind.WITHDRAW_INTERNAL) {
    			IERC20(asset).transfer(recipient, amount);
    			balanceOf[asset][sender] = balanceOf[asset][sender].sub(amount);
    		}
    		else if  (ops[i].kind ==  UserBalanceOpKind.TRANSFER_INTERNAL) {
    			balanceOf[asset][sender] = balanceOf[asset][sender].sub(amount);
    			balanceOf[asset][recipient] = balanceOf[asset][recipient].add(amount);
    		}
    		else if (ops[i].kind ==  UserBalanceOpKind.TRANSFER_EXTERNAL) {
    			IERC20(asset).transferFrom(sender,recipient,amount);		
    		}
    	}
    }

    // totalAssetOfUSer(IERC20 asset, addres user) = asset.balanceOf(user)  + symbolicVault.balanceOf(asset,user)     //nned a dummy ERC for it
    // dispatcher

}
