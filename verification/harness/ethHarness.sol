pragma solidity ^0.7.0;
pragma experimental ABIEncoderV2;

import "./simplifiedVaultHarness.sol";

contract ethHarness is simplifiedVaultHarness {
    /*
    This harness exposes information used by rules caring about the internal balance.
    */

    constructor(IAuthorizer authorizer,
        IWETH weth,
        uint256 emergencyPeriod,
        uint256 emergencyPeriodCheckExtension
    ) simplifiedVaultHarness(authorizer, weth, emergencyPeriod, emergencyPeriodCheckExtension) { }

    function Harness_vaultEthBalance() public view returns (uint256) {
        return address(this).balance;
    }

    mapping(address => uint256) receive_asset_counter;

    function Harness_wrapper_reveive_asset(address token) public {
        uint256 old_count = receive_asset_counter[token];
        uint256 new_count = old_count + 1;
        require(new_count > old_count);
        receive_asset_counter[token] = new_count;
    }

    function Harness_get_receive_asset_counter(address token) public view returns (uint256) {
        return receive_asset_counter[token];
    }

}