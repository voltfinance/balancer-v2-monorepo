// SPDX-License-Identifier: GPL-3.0-or-later
// Copyright (C) 2015, 2016, 2017 Dapphub

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

// import "../lib/openzeppelin/AccessControl.sol";

// import "../vault/interfaces/IWETH.sol";

// contract WETH is AccessControl, IWETH {
contract WETH {
    // bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");

    // string public name = "Wrapped Ether";
    // string public symbol = "WETH";
    // uint8 public decimals = 18;

    event Deposit(address indexed dst, uint256 wad);
    event Withdrawal(address indexed src, uint256 wad);

    // mapping(address => uint256) public override balanceOf;
    mapping(address => uint256) public balanceOf;
    // mapping(address => mapping(address => uint256)) public override allowance;
    mapping(address => mapping(address => uint256)) public allowance;

    constructor(address minter) {
        // _setupRole(MINTER_ROLE, minter);
    }

    receive() external payable {
        deposit();
    }

    // function deposit() public payable override {
    function deposit() public payable {
        balanceOf[msg.sender] += msg.value;
    }

    // function withdraw(uint256 wad) public override {
    function withdraw(uint256 wad) public {
        require(balanceOf[msg.sender] >= wad, "INSUFFICIENT_BALANCE");
        balanceOf[msg.sender] -= wad;
        msg.sender.transfer(wad);
    }

    // // For testing purposes - this creates WETH that cannot be redeemed for ETH via 'withdraw'
    // function mint(address destinatary, uint256 amount) external {
    //     require(hasRole(MINTER_ROLE, msg.sender), "NOT_MINTER");
    //     balanceOf[destinatary] += amount;
    //     emit Deposit(destinatary, amount);
    // }

    // function totalSupply() public view override returns (uint256) {
    function totalSupply() public view returns (uint256) {
        return address(this).balance;
    }

    // function approve(address guy, uint256 wad) public override returns (bool) {
    function approve(address guy, uint256 wad) public returns (bool) {
        allowance[msg.sender][guy] = wad;
        return true;
    }

    // function transfer(address dst, uint256 wad) public override returns (bool) {
    function transfer(address dst, uint256 wad) public returns (bool) {
        return transferFrom(msg.sender, dst, wad);
    }

    function transferFrom(
        address src,
        address dst,
        uint256 wad
    // ) public override returns (bool) {
    ) public returns (bool) {
        require(balanceOf[src] >= wad, "INSUFFICIENT_BALANCE");
        require(balanceOf[dst] + wad >= balanceOf[dst], "overflow");

        if (src != msg.sender && allowance[src][msg.sender] != uint256(-1)) {
            require(allowance[src][msg.sender] >= wad, "INSUFFICIENT_ALLOWANCE");
            allowance[src][msg.sender] -= wad;
        }

        balanceOf[src] -= wad;
        balanceOf[dst] += wad;

        return true;
    }
}
