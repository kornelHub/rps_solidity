from scripts.helpful_scripts import get_account
from scripts.deploy import deploy_rps_token_and_game
from brownie import reverts
import pytest
from web3 import Web3


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_deposit_funds_positive():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    account = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    # Act
    deposit_tx = rps_game.depositFunds({"from":account, "value": amount_deposited})
    deposit_tx.wait(1)
    # Assert
    assert rps_game.getDepositedFundsValue(account.address) == amount_deposited * rps_game.getEthRpsRatio()
    assert deposit_tx.events['fundsDepositedEvent']['_addressOfAccount'] == account.address
    assert deposit_tx.events['fundsDepositedEvent']['_amountDepositedInEth'] == amount_deposited


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_deposit_funds_below_minimal_value_fail():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    account = get_account(index=1)
    amount_deposited = Web3.toWei(0.00001, 'ether')
    contract_balance_of_rps_token = rps_token.balanceOf(rps_game.address)
    # Act/Assert
    with reverts("Minimal value to deposit is 0.0001 ETH!"):
        rps_game.depositFunds({"from":account, "value": amount_deposited}).wait(1)
    assert rps_token.balanceOf(rps_game.address) == contract_balance_of_rps_token


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_multiple_deposit_funds_positive():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    account = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    contract_balance_of_rps_token = rps_token.balanceOf(rps_game.address)
    # Act / Assert
    deposit_tx = rps_game.depositFunds({"from":account, "value": amount_deposited})
    deposit_tx.wait(1)
    assert rps_game.getDepositedFundsValue(account.address) == amount_deposited * rps_game.getEthRpsRatio()
    assert deposit_tx.events['fundsDepositedEvent']['_addressOfAccount'] == account.address
    assert deposit_tx.events['fundsDepositedEvent']['_amountDepositedInEth'] == amount_deposited

    contract_balance_of_rps_token = rps_token.balanceOf(rps_game.address)
    deposit_tx = rps_game.depositFunds({"from": account, "value": amount_deposited})
    deposit_tx.wait(1)
    assert rps_game.getDepositedFundsValue(account.address) == amount_deposited * 2 * rps_game.getEthRpsRatio()
    assert deposit_tx.events['fundsDepositedEvent']['_addressOfAccount'] == account.address
    assert deposit_tx.events['fundsDepositedEvent']['_amountDepositedInEth'] == amount_deposited


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_withdraw_funds_positive():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    account = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_game.depositFunds({"from":account, "value": amount_deposited}).wait(1)
    assert rps_game.getDepositedFundsValue(account.address) == amount_deposited * rps_game.getEthRpsRatio()
    # Act
    withdraw_tx = rps_game.withdrawFunds({"from": account})
    withdraw_tx.wait(1)
    # Assert
    assert rps_game.getDepositedFundsValue(account.address) == 0
    assert rps_token.balanceOf(rps_game.address) == 0
    assert withdraw_tx.events['fundsWithdrawnEvent']['_addressOfAccount'] == account
    assert withdraw_tx.events['fundsWithdrawnEvent']['_amountWithdrawnInEth'] == amount_deposited


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_withdraw_with_zero_funds_fail():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    account = get_account(index=1)
    # Act / Assert
    with reverts('You dont have funds deposited in this contract!'):
        rps_game.withdrawFunds({"from": account}).wait(1)


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_withdraw_after_joining_game_fail():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    player_account_1 = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_game.depositFunds({"from": player_account_1, "value": amount_deposited}).wait(1)
    # Act / Assert
    rps_game.joinGame(1, 1, {'from': player_account_1})
    with reverts('To withdraw money, you cant be waiting for game. Please quite game!'):
        rps_game.withdrawFunds({"from": player_account_1}).wait(1)


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_update_bid_values_positive():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    low_bid = rps_game.getLowBidValue()
    medium_bid = rps_game.getMediumBidValue()
    high_bid = rps_game.getHighBidValue()
    increment_value = 1
    # Act / Assert
    rps_game.updateLowBidValue(low_bid + increment_value, {"from": owner_acc}).wait(1)
    assert rps_game.getLowBidValue() == low_bid + increment_value
    assert rps_game.getLinkBidWithValues(0) == low_bid + increment_value

    rps_game.updateMediumBidValue(medium_bid + increment_value, {"from": owner_acc}).wait(1)
    assert rps_game.getMediumBidValue() == medium_bid + increment_value
    assert rps_game.getLinkBidWithValues(1) == medium_bid + increment_value

    rps_game.updateHighBidValue(high_bid + increment_value, {"from": owner_acc}).wait(1)
    assert  rps_game.getHighBidValue() == high_bid + increment_value
    assert rps_game.getLinkBidWithValues(2) == high_bid + increment_value


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_update_bid_value_bad_owner_fail():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    not_owner_account = get_account(index=1)
    low_bid = rps_game.getLowBidValue()
    medium_bid = rps_game.getMediumBidValue()
    high_bid = rps_game.getHighBidValue()
    increment_value = 1
    # Act / Assert
    with reverts('Ownable: caller is not the owner'):
        rps_game.updateLowBidValue(low_bid + increment_value, {"from": not_owner_account}).wait(1)
    with reverts('Ownable: caller is not the owner'):
        rps_game.updateMediumBidValue(medium_bid + increment_value, {"from": not_owner_account}).wait(1)
    with reverts('Ownable: caller is not the owner'):
        rps_game.updateHighBidValue(high_bid + increment_value, {"from": not_owner_account}).wait(1)

    assert low_bid == rps_game.getLowBidValue()
    assert rps_game.getLinkBidWithValues(0) == rps_game.getLowBidValue()
    assert medium_bid == rps_game.getMediumBidValue()
    assert rps_game.getLinkBidWithValues(1) == rps_game.getMediumBidValue()
    assert high_bid == rps_game.getHighBidValue()
    assert rps_game.getLinkBidWithValues(2) == rps_game.getHighBidValue()


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_join_game_positive():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    player_account_1 = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_game.depositFunds({"from":player_account_1, "value": amount_deposited}).wait(1)
    # Act
    join_tx = rps_game.joinGame(1,1, {'from': player_account_1})
    join_tx.wait(1)
    # Assert
    assert rps_game.isPlayerInQueue(player_account_1.address)
    assert join_tx.events['joinedQueueEvent']['_addressOfPlayer'] == player_account_1
    assert join_tx.events['joinedQueueEvent']['_chosenBid'] == 1


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_join_game_no_funds_fail():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    player_account_1 = get_account(index=1)
    # Act / Assert
    with reverts('You dont have enough funds to join game with this bid!'):
        rps_game.joinGame(1, 1, {'from': player_account_1})


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_join_game_multiple_joins_fail():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    player_account_1 = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_game.depositFunds({"from": player_account_1, "value": amount_deposited}).wait(1)
    rps_game.joinGame(1, 1, {'from': player_account_1})
    # Act / Assert
    with reverts('You cant wait for 2 games at the same time! Quite queue or wait for match!'):
        rps_game.joinGame(1, 1, {'from': player_account_1})


test_choose_winner_and_transfer_reward_data = [
    (0, 0, 0, 'draw'), (0, 1, 0, 'p2'), (0, 2, 0, 'p1'),
    (1, 0, 1, 'p1'), (1, 1, 1, 'draw'), (1, 2, 1, 'p2'),
    (2, 0, 2, 'p2'), (2, 1, 2, 'p1'), (2, 2, 2, 'draw'),
]

@pytest.mark.require_network("development", "ganache", "ganache_local")
@pytest.mark.parametrize("player_1_symbol,"
                         " player_2_symbol,"
                         " bid_value, winner",
                         test_choose_winner_and_transfer_reward_data)
def test_choose_winner_and_transfer_reward(player_1_symbol, player_2_symbol, bid_value, winner):
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    player_account_1 = get_account(index=1)
    player_account_2 = get_account(index=2)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_game.depositFunds({"from":player_account_1, "value": amount_deposited}).wait(1)
    rps_game.depositFunds({"from": player_account_2, "value": amount_deposited}).wait(1)
    player_balance_1 = rps_game.getDepositedFundsValue(player_account_1.address)
    player_balance_2 = rps_game.getDepositedFundsValue(player_account_2.address)
    bid_value_dict = {
        0: rps_game.getLowBidValue(),
        1: rps_game.getMediumBidValue(),
        2: rps_game.getHighBidValue()
    }
    # Act
    if winner == 'p1':
        rps_token.approve(rps_game.address, bid_value_dict[bid_value], {'from': player_account_2}).wait(1)
    elif winner == 'p2':
        rps_token.approve(rps_game.address, bid_value_dict[bid_value], {'from': player_account_1}).wait(1)

    rps_game.joinGame(player_1_symbol, bid_value, {'from': player_account_1}).wait(1)
    join_tx = rps_game.joinGame(player_2_symbol, bid_value, {'from': player_account_2})
    join_tx.wait(1)
    # Assert
    if (player_1_symbol == 0):
        if (player_2_symbol == 0):
            assert rps_game.getDepositedFundsValue(player_account_1.address) == player_balance_1
            assert rps_game.getDepositedFundsValue(player_account_2.address) == player_balance_2
            assert join_tx.events['matchEndedEvent']['_matchResult'] == 'Draw'
        elif (player_2_symbol == 1):
            assert rps_game.getDepositedFundsValue(player_account_1.address) \
                   == player_balance_1 - bid_value_dict[bid_value]
            assert rps_game.getDepositedFundsValue(player_account_2.address) \
                   == player_balance_2 + bid_value_dict[bid_value]
            assert join_tx.events['matchEndedEvent']['_matchResult'] == 'Winner: player2'
        elif (player_2_symbol == 2):
            assert rps_game.getDepositedFundsValue(player_account_1.address) \
                   == player_balance_1 + bid_value_dict[bid_value]
            assert rps_game.getDepositedFundsValue(player_account_2.address) \
                   == player_balance_2 - bid_value_dict[bid_value]
            assert join_tx.events['matchEndedEvent']['_matchResult'] == 'Winner: player1'

    if (player_1_symbol == 1):
        if (player_2_symbol == 1):
            assert rps_game.getDepositedFundsValue(player_account_1.address) == player_balance_1
            assert rps_game.getDepositedFundsValue(player_account_2.address) == player_balance_2
            assert join_tx.events['matchEndedEvent']['_matchResult'] == 'Draw'
        elif (player_2_symbol == 0):
            assert rps_game.getDepositedFundsValue(player_account_1.address) \
                   == player_balance_1 + bid_value_dict[bid_value]
            assert rps_game.getDepositedFundsValue(player_account_2.address) \
                   == player_balance_2 - bid_value_dict[bid_value]
            assert join_tx.events['matchEndedEvent']['_matchResult'] == 'Winner: player1'
        elif (player_2_symbol == 2):
            assert rps_game.getDepositedFundsValue(player_account_1.address) \
                   == player_balance_1 - bid_value_dict[bid_value]
            assert rps_game.getDepositedFundsValue(player_account_2.address) \
                   == player_balance_2 + bid_value_dict[bid_value]
            assert join_tx.events['matchEndedEvent']['_matchResult'] == 'Winner: player2'

    if (player_1_symbol == 2):
        if (player_2_symbol == 2):
            assert rps_game.getDepositedFundsValue(player_account_1.address) == player_balance_1
            assert rps_game.getDepositedFundsValue(player_account_2.address) == player_balance_2
            assert join_tx.events['matchEndedEvent']['_matchResult'] == 'Draw'
        elif (player_2_symbol == 0):
            assert rps_game.getDepositedFundsValue(player_account_1.address) \
                   == player_balance_1 - bid_value_dict[bid_value]
            assert rps_game.getDepositedFundsValue(player_account_2.address) \
                   == player_balance_2 + bid_value_dict[bid_value]
            assert join_tx.events['matchEndedEvent']['_matchResult'] == 'Winner: player2'
        elif (player_2_symbol == 1):
            assert rps_game.getDepositedFundsValue(player_account_1.address) \
                   == player_balance_1 + bid_value_dict[bid_value]
            assert rps_game.getDepositedFundsValue(player_account_2.address) \
                   == player_balance_2 - bid_value_dict[bid_value]
            assert join_tx.events['matchEndedEvent']['_matchResult'] == 'Winner: player1'

    assert join_tx.events['matchEndedEvent']['_player1Address'] == player_account_1.address
    assert join_tx.events['matchEndedEvent']['_player1Symbol'] == player_1_symbol
    assert join_tx.events['matchEndedEvent']['_player2Address'] == player_account_2.address
    assert join_tx.events['matchEndedEvent']['_player2Symbol'] == player_2_symbol
    assert join_tx.events['matchEndedEvent']['_bidValue'] == bid_value


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_quite_queue_positive():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    player_account_1 = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_game.depositFunds({"from":player_account_1, "value": amount_deposited}).wait(1)
    rps_game.joinGame(1,1, {'from': player_account_1})
    assert rps_game.isPlayerInQueue(player_account_1.address)
    # Act
    rps_game.quiteQueue({"from": player_account_1})
    # Assert
    assert rps_game.isPlayerInQueue(player_account_1.address) == False


@pytest.mark.require_network("development", "ganache", "ganache_local")
def test_quite_queue_without_joining_game_fail():
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    player_account_1 = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_game.depositFunds({"from":player_account_1, "value": amount_deposited}).wait(1)
    # Act / Arrange
    with reverts('You cant quite queue, if you arent in it!'):
        rps_game.quiteQueue({"from": player_account_1})