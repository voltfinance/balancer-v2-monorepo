pragma solidity ^0.7.0;

import "../munged/solidity-utils/contracts/openzeppelin/ERC20.sol";

contract SymbolicERC20B is ERC20 {

    constructor(string memory name_, string memory symbol_) ERC20(name_, symbol_) { }
}