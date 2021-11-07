// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";

contract RPS_Token is ERC20 {
    address private rpsGameAddress;
    address private ownerAddress;

    constructor() ERC20('RPS_Token', 'RPS'){
        _mint(msg.sender, 1000000000000000000);
        ownerAddress = msg.sender;
    }

    function createNewTokensForGame(address _addressToTransfer, uint256 _amount) external onlyRpsGame(msg.sender){
        _mint(_addressToTransfer, _amount);
    }

    function destroyTokens(address _addressToTransfer, uint256 _amount) external onlyRpsGame(msg.sender){
        _burn(_addressToTransfer, _amount);
    }

    function setRPSGameAddress(address _rpsGameAddress) public {
        require(msg.sender == ownerAddress, "To call this function you need to be owner of this contract!");
        rpsGameAddress = _rpsGameAddress;
    }

    modifier onlyRpsGame(address _addressToCheck){
        require(_addressToCheck == rpsGameAddress, "This function can call only RPS Game contract!");
        _;
    }
}