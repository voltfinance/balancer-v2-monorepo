// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity ^0.7.0;

import "@balancer-labs/v2-solidity-utils/contracts/openzeppelin/ERC20.sol";

contract MockfUSD is ERC20 {
    constructor() ERC20("Fuse Dollar", "fUSD") {}

    function mint(address recipient, uint256 amount) public {
        _mint(recipient, amount);
    }

    function burn(uint256 amount) public {
        _burn(msg.sender, amount);
    }
}
