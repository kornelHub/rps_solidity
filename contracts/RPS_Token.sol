// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract RPS_Token is ERC20 {
    constructor() ERC20('RPS_Token', 'RPS'){
        _mint(msg.sender, 1000000000000000000);
    }

    function createNewTokensForGame(uint256 _amount) external{
        _mint(msg.sender, _amount);
    }

    function destroyTokens(uint256 _amount) external{
        _burn(msg.sender, _amount);
    }
}
