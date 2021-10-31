// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./RPS_Token.sol";

contract RPS_Game is Ownable{
    mapping(address => uint256) private balancesOfUsers;
    RPS_Token public rpsToken;
    // 1 ETH = 10000 RPS
    uint256 private ethRpsRatio = 100000000000000;
    enum RPS_AVAILABLE_SYMBOL{ROCK, PAPER, SCISSORS}
    uint256 private lowBid;
    uint256 private mediumBid;
    uint256 private highBid;
    enum RPS_AVAILABLE_BID{LOW_BID, MEDIUM_BID, HIGH_BID}
    mapping(RPS_AVAILABLE_BID => uint256) private linkBidWithValues;

    mapping(RPS_AVAILABLE_BID => address) private linkBidWithWaitingPlayerAddress;
    mapping(address => RPS_AVAILABLE_SYMBOL) private linkAddressOfWaitingPlayerWithChosenMark;
    mapping(address => bool) private isPlayerWaitingForMatch;


    constructor(address _rpsToken){
        rpsToken = RPS_Token(_rpsToken);
        lowBid = 1;
        mediumBid = 5;
        highBid = 10;
        linkBidWithValues[RPS_AVAILABLE_BID.LOW_BID] = lowBid;
        linkBidWithValues[RPS_AVAILABLE_BID.MEDIUM_BID] = mediumBid;
        linkBidWithValues[RPS_AVAILABLE_BID.HIGH_BID] = highBid;
    }

    function depositFunds() public payable {
        require(msg.value >= 100000000000000, 'Minimal value to deposit is 0.0001 ETH!');
        // 1 ETH = 10000 RPS
        uint256 valueInRPS = msg.value / ethRpsRatio;
        rpsToken.createNewTokensForGame(valueInRPS);
        balancesOfUsers[msg.sender] = balancesOfUsers[msg.sender] + valueInRPS;
    }

    function withdrawFunds() public payable {
        require(balancesOfUsers[msg.sender] > 0, 'You dont have funds deposited in this contract!');
        payable(msg.sender).transfer(balancesOfUsers[msg.sender] * ethRpsRatio);
        rpsToken.destroyTokens(balancesOfUsers[msg.sender]);
        balancesOfUsers[msg.sender] = 0;
    }

    function getDepositedFundsValue(address _userToCheck) public view returns(uint256) {
        return balancesOfUsers[_userToCheck];
    }

    function getEthRpsRatio() public view returns(uint256) {
        return ethRpsRatio;
    }

    function getLowBidValue() public view returns(uint256) {
        return lowBid;
    }

    function getMediumBidValue() public view returns(uint256) {
        return mediumBid;
    }

    function getHighBidValue() public view returns(uint256) {
        return highBid;
    }

    function updateLowBidValue(uint256 _newValue) public onlyOwner {
        lowBid = _newValue;
        linkBidWithValues[RPS_AVAILABLE_BID.LOW_BID] = _newValue;
    }

    function updateMediumBidValue(uint256 _newValue) public onlyOwner {
        mediumBid = _newValue;
        linkBidWithValues[RPS_AVAILABLE_BID.MEDIUM_BID] = _newValue;
    }

    function updateHighBidValue(uint256 _newValue) public onlyOwner {
        highBid = _newValue;
        linkBidWithValues[RPS_AVAILABLE_BID.HIGH_BID] = _newValue;
    }

    function getLinkBidWithValues(RPS_AVAILABLE_BID _bid) public view returns(uint256){
        return linkBidWithValues[_bid];
    }

    function isPlayerInQueue(address _playerToCheck) public view returns(bool){
        return isPlayerWaitingForMatch[_playerToCheck];
    }

    function joinGame(RPS_AVAILABLE_SYMBOL _chosenSymbol, RPS_AVAILABLE_BID _chosenBid) public{
        // add some require functions to check if user have enough funds to join game
        require(getDepositedFundsValue(msg.sender) >= getLinkBidWithValues(_chosenBid), "You dont have enough funds to join game with this bid!");
        require(isPlayerWaitingForMatch[msg.sender] == false, "You cant wait for 2 games at the same time! Quite queue or wait for match!");
        // no waiting player with selected bid
        if (linkBidWithWaitingPlayerAddress[_chosenBid] == address(0x0)){
            linkBidWithWaitingPlayerAddress[_chosenBid] = msg.sender;
            linkAddressOfWaitingPlayerWithChosenMark[msg.sender] = _chosenSymbol;
            isPlayerWaitingForMatch[msg.sender] = true;
        } else { //there is waiting player for selected bid
            address _player1 = linkBidWithWaitingPlayerAddress[_chosenBid];
            delete linkBidWithWaitingPlayerAddress[_chosenBid];
            RPS_AVAILABLE_SYMBOL _chosenSymbol1 = linkAddressOfWaitingPlayerWithChosenMark[_player1];
            delete linkAddressOfWaitingPlayerWithChosenMark[_player1];
            delete isPlayerWaitingForMatch[_player1];
            chooseWinnerAndTransferReward(_player1, _chosenSymbol1, msg.sender, _chosenSymbol, _chosenBid);
        }
    }

    function chooseWinnerAndTransferReward(
        address _player1,
        RPS_AVAILABLE_SYMBOL _chosenSymbol1,
        address _player2,
        RPS_AVAILABLE_SYMBOL _chosenSymbol2,
        RPS_AVAILABLE_BID _chosenBid) internal {
        if (_chosenSymbol1 == RPS_AVAILABLE_SYMBOL.ROCK){
            if (_chosenSymbol2 == RPS_AVAILABLE_SYMBOL.PAPER){
                balancesOfUsers[_player1] = balancesOfUsers[_player1] - linkBidWithValues[_chosenBid];
                balancesOfUsers[_player2] = balancesOfUsers[_player2] + linkBidWithValues[_chosenBid];
            } else if (_chosenSymbol2 == RPS_AVAILABLE_SYMBOL.SCISSORS){
                balancesOfUsers[_player1] = balancesOfUsers[_player1] + linkBidWithValues[_chosenBid];
                balancesOfUsers[_player2] = balancesOfUsers[_player2] - linkBidWithValues[_chosenBid];
            }
        }
        if (_chosenSymbol1 == RPS_AVAILABLE_SYMBOL.PAPER){
            if (_chosenSymbol2 == RPS_AVAILABLE_SYMBOL.ROCK){
                balancesOfUsers[_player1] = balancesOfUsers[_player1] + linkBidWithValues[_chosenBid];
                balancesOfUsers[_player2] = balancesOfUsers[_player2] - linkBidWithValues[_chosenBid];
            } else if (_chosenSymbol2 == RPS_AVAILABLE_SYMBOL.SCISSORS){
                balancesOfUsers[_player1] = balancesOfUsers[_player1] - linkBidWithValues[_chosenBid];
                balancesOfUsers[_player2] = balancesOfUsers[_player2] + linkBidWithValues[_chosenBid];
            }
        }
        if (_chosenSymbol1 == RPS_AVAILABLE_SYMBOL.SCISSORS){
            if (_chosenSymbol2 == RPS_AVAILABLE_SYMBOL.ROCK){
                balancesOfUsers[_player1] = balancesOfUsers[_player1] - linkBidWithValues[_chosenBid];
                balancesOfUsers[_player2] = balancesOfUsers[_player2] + linkBidWithValues[_chosenBid];
            } else if (_chosenSymbol2 == RPS_AVAILABLE_SYMBOL.PAPER){
                balancesOfUsers[_player1] = balancesOfUsers[_player1] + linkBidWithValues[_chosenBid];
                balancesOfUsers[_player2] = balancesOfUsers[_player2] - linkBidWithValues[_chosenBid];
            }
        }
    }

    function quiteQueue() public {
        require(isPlayerWaitingForMatch[msg.sender] == true, "You cant quite queue, if you arent in it!");
        if (linkBidWithWaitingPlayerAddress[RPS_AVAILABLE_BID.LOW_BID] == msg.sender){
            delete linkBidWithWaitingPlayerAddress[RPS_AVAILABLE_BID.LOW_BID];
        } else if (linkBidWithWaitingPlayerAddress[RPS_AVAILABLE_BID.MEDIUM_BID] == msg.sender){
            delete linkBidWithWaitingPlayerAddress[RPS_AVAILABLE_BID.MEDIUM_BID];
        } else if (linkBidWithWaitingPlayerAddress[RPS_AVAILABLE_BID.HIGH_BID] == msg.sender) {
            delete linkBidWithWaitingPlayerAddress[RPS_AVAILABLE_BID.HIGH_BID];
        }
        delete isPlayerWaitingForMatch[msg.sender];
        delete linkAddressOfWaitingPlayerWithChosenMark[msg.sender];
    }
}