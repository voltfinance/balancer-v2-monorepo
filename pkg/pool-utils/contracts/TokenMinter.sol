// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.7.0;

import "@balancer-labs/v2-solidity-utils/contracts/openzeppelin/ERC20Permit.sol";
import "@balancer-labs/v2-solidity-utils/contracts/openzeppelin/SafeMath.sol";
import "@balancer-labs/v2-solidity-utils/contracts/misc/IfUSD.sol";
import "@balancer-labs/v2-vault/contracts/interfaces/IVault.sol";

contract TokenMinter {
    using SafeMath for uint256;

    IfUSD private immutable _token;
    IVault private immutable _vault;

    uint256 private _totalSupply = 0;

    constructor(IfUSD token, IVault vault) {
        _token = token;
        _vault = vault;
    }

    function getVault() public view returns (IVault) {
        return _vault;
    }

    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address account) public view returns (uint256) {
        return _token.balanceOf(account);
    }

    function name() public view returns (string memory) {
        return _token.name();
    }

    function symbol() public view returns (string memory) {
        return _token.symbol();
    }

    function decimals() public view returns (uint256) {
        return _token.decimals();
    }


    // internal functions
    function _transferFrom(address sender, address recipient, uint256 amount) internal {
        _token.transferFrom(sender, recipient, amount);
    }

    function _mintTokens(address recipient, uint256 amount) internal {
        _totalSupply = _totalSupply.add(amount);
        _token.mint(recipient, amount);
        _token.approve(msg.sender, uint256(-1));
    }

    function _burnTokens(address sender, uint256 amount) internal {
        _totalSupply = _totalSupply.sub(amount);
        _token.burn(amount);
    }
}
