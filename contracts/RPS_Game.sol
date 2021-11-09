// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./RPS_Token.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract RPS_Game is Ownable{
    RPS_Token public rpsToken;
    // 1 ETH = 10000 RPS
    uint256 private ethRpsRatio = 10000;
    enum RPS_AVAILABLE_SYMBOL{ROCK, PAPER, SCISSORS}
    uint256 private lowBid;
    uint256 private mediumBid;
    uint256 private highBid;
    enum RPS_AVAILABLE_BID{LOW_BID, MEDIUM_BID, HIGH_BID}
    mapping(RPS_AVAILABLE_BID => uint256) private linkBidWithValues;

    mapping(RPS_AVAILABLE_BID => address) private linkBidWithWaitingPlayerAddress;
    mapping(address => RPS_AVAILABLE_SYMBOL) private linkAddressOfWaitingPlayerWithChosenMark;
    mapping(address => bool) private isPlayerWaitingForMatch;

    event fundsDepositedEvent(address _addressOfAccount, uint256 _amountDepositedInEth);
    event fundsWithdrawnEvent(address _addressOfAccount, uint256 _amountWithdrawnInEth);
    event joinedQueueEvent(address _addressOfPlayer, RPS_AVAILABLE_BID _chosenBid);
    event quiteQueueEvent(address _addressOfPlayer, RPS_AVAILABLE_BID _chosenBid);
    event matchEndedEvent(
        address _player1Address,
        RPS_AVAILABLE_SYMBOL _player1Symbol,
        address _player2Address,
        RPS_AVAILABLE_SYMBOL _player2Symbol,
        RPS_AVAILABLE_BID _bidValue,
        string _matchResult);


    constructor(address _rpsToken){
        rpsToken = RPS_Token(_rpsToken);
        lowBid = 1000000000000000000;
        mediumBid = 5000000000000000000;
        highBid = 10000000000000000000;
        linkBidWithValues[RPS_AVAILABLE_BID.LOW_BID] = lowBid;
        linkBidWithValues[RPS_AVAILABLE_BID.MEDIUM_BID] = mediumBid;
        linkBidWithValues[RPS_AVAILABLE_BID.HIGH_BID] = highBid;
    }

    function depositFunds() public payable {
        require(msg.value >= 100000000000000, 'Minimal value to deposit is 0.0001 ETH!');
        // 1 ETH = 10000 RPS
        uint256 valueInRPS = msg.value * ethRpsRatio;
        rpsToken.createNewTokensForGame(msg.sender, valueInRPS);
        emit fundsDepositedEvent(msg.sender, msg.value);
    }

    function withdrawFunds() public {
        require(getDepositedFundsValue(msg.sender) > 0, 'You dont have funds deposited in this contract!');
        require(isPlayerInQueue(msg.sender) == false, "To withdraw money, you cant be waiting for game. Please quite game!");
        uint256 amountToWithdraw = getDepositedFundsValue(msg.sender) / ethRpsRatio;
        payable(msg.sender).transfer(amountToWithdraw);
        rpsToken.destroyTokens(msg.sender, getDepositedFundsValue(msg.sender));
        emit fundsWithdrawnEvent(msg.sender, amountToWithdraw);
    }

    function getDepositedFundsValue(address _userToCheck) public view returns(uint256) {
        return rpsToken.balanceOf(_userToCheck);
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
        require(getDepositedFundsValue(msg.sender) >= getLinkBidWithValues(_chosenBid), "You dont have enough funds to join game with this bid!");
        require(isPlayerWaitingForMatch[msg.sender] == false, "You cant wait for 2 games at the same time! Quite queue or wait for match!");
        // no waiting player with selected bid
        if (linkBidWithWaitingPlayerAddress[_chosenBid] == address(0x0)){
            linkBidWithWaitingPlayerAddress[_chosenBid] = msg.sender;
            linkAddressOfWaitingPlayerWithChosenMark[msg.sender] = _chosenSymbol;
            isPlayerWaitingForMatch[msg.sender] = true;
            emit joinedQueueEvent(msg.sender, _chosenBid);
        } else { //there is waiting player for selected bid
            address _player1 = linkBidWithWaitingPlayerAddress[_chosenBid];
            delete linkBidWithWaitingPlayerAddress[_chosenBid];
            RPS_AVAILABLE_SYMBOL _chosenSymbol1 = linkAddressOfWaitingPlayerWithChosenMark[_player1];
            delete linkAddressOfWaitingPlayerWithChosenMark[_player1];
            delete isPlayerWaitingForMatch[_player1];
            emit joinedQueueEvent(msg.sender, _chosenBid);
            chooseWinnerAndTransferReward(_player1, _chosenSymbol1, msg.sender, _chosenSymbol, _chosenBid);
        }
    }

    function chooseWinnerAndTransferReward(
        address _player1,
        RPS_AVAILABLE_SYMBOL _chosenSymbol1,
        address _player2,
        RPS_AVAILABLE_SYMBOL _chosenSymbol2,
        RPS_AVAILABLE_BID _chosenBid) internal {
        string memory matchResult;
        if (_chosenSymbol1 == RPS_AVAILABLE_SYMBOL.ROCK){
            if (_chosenSymbol2 == RPS_AVAILABLE_SYMBOL.PAPER){
                rpsToken.transferFrom(_player1, _player2, linkBidWithValues[_chosenBid]);
                matchResult = 'Winner: player2';
            } else if (_chosenSymbol2 == RPS_AVAILABLE_SYMBOL.SCISSORS){
                rpsToken.transferFrom(_player2, _player1, linkBidWithValues[_chosenBid]);
                matchResult = 'Winner: player1';
            } else {
                matchResult = 'Draw';
            }
        } else if (_chosenSymbol1 == RPS_AVAILABLE_SYMBOL.PAPER){
            if (_chosenSymbol2 == RPS_AVAILABLE_SYMBOL.ROCK){
                rpsToken.transferFrom(_player2, _player1, linkBidWithValues[_chosenBid]);
                matchResult = 'Winner: player1';
            } else if (_chosenSymbol2 == RPS_AVAILABLE_SYMBOL.SCISSORS){
                rpsToken.transferFrom(_player1, _player2, linkBidWithValues[_chosenBid]);
                matchResult = 'Winner: player2';
            } else {
                matchResult = 'Draw';
            }
        } else if (_chosenSymbol1 == RPS_AVAILABLE_SYMBOL.SCISSORS){
            if (_chosenSymbol2 == RPS_AVAILABLE_SYMBOL.ROCK){
                rpsToken.transferFrom(_player1, _player2, linkBidWithValues[_chosenBid]);
                matchResult = 'Winner: player2';
            } else if (_chosenSymbol2 == RPS_AVAILABLE_SYMBOL.PAPER){
                rpsToken.transferFrom(_player2, _player1, linkBidWithValues[_chosenBid]);
                matchResult = 'Winner: player1';
            } else {
                matchResult = 'Draw';
            }
        }
        emit matchEndedEvent(_player1, _chosenSymbol1, _player2, _chosenSymbol2, _chosenBid, matchResult);
    }

    function quiteQueue() public {
        require(isPlayerWaitingForMatch[msg.sender] == true, "You cant quite queue, if you arent in it!");
        if (linkBidWithWaitingPlayerAddress[RPS_AVAILABLE_BID.LOW_BID] == msg.sender){
            delete linkBidWithWaitingPlayerAddress[RPS_AVAILABLE_BID.LOW_BID];
            emit quiteQueueEvent(msg.sender, RPS_AVAILABLE_BID.LOW_BID);
        } else if (linkBidWithWaitingPlayerAddress[RPS_AVAILABLE_BID.MEDIUM_BID] == msg.sender){
            delete linkBidWithWaitingPlayerAddress[RPS_AVAILABLE_BID.MEDIUM_BID];
            emit quiteQueueEvent(msg.sender, RPS_AVAILABLE_BID.MEDIUM_BID);
        } else if (linkBidWithWaitingPlayerAddress[RPS_AVAILABLE_BID.HIGH_BID] == msg.sender) {
            delete linkBidWithWaitingPlayerAddress[RPS_AVAILABLE_BID.HIGH_BID];
            emit quiteQueueEvent(msg.sender, RPS_AVAILABLE_BID.HIGH_BID);
        }
        delete isPlayerWaitingForMatch[msg.sender];
        delete linkAddressOfWaitingPlayerWithChosenMark[msg.sender];
    }
}