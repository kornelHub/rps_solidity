from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.deploy import deploy_rps_token_and_game
from brownie import network, exceptions
import pytest
from web3 import Web3


def test_deposit_funds_positive():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    account = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    contract_balance_of_rps_token = rps_token.balanceOf(rps_game.address)
    # Act
    rps_game.depositFunds({"from":account, "value": amount_deposited}).wait(1)
    # Assert
    assert rps_game.getDepositedFundsValue(account.address) == amount_deposited / rps_game.getEthRpsRatio()
    assert rps_token.balanceOf(rps_game.address) == contract_balance_of_rps_token + (amount_deposited / rps_game.getEthRpsRatio())


def test_deposit_funds_below_minimal_value_fail():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    account = get_account(index=1)
    amount_deposited = Web3.toWei(0.00001, 'ether')
    contract_balance_of_rps_token = rps_token.balanceOf(rps_game.address)
    # Act/Assert
    with pytest.raises(exceptions.VirtualMachineError):
        rps_game.depositFunds({"from":account, "value": amount_deposited}).wait(1)
    assert rps_token.balanceOf(rps_game.address) == contract_balance_of_rps_token


def test_multiple_deposit_funds_positive():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    account = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    contract_balance_of_rps_token = rps_token.balanceOf(rps_game.address)
    # Act / Assert
    rps_game.depositFunds({"from":account, "value": amount_deposited}).wait(1)
    assert rps_game.getDepositedFundsValue(account.address) == amount_deposited / rps_game.getEthRpsRatio()
    assert rps_token.balanceOf(rps_game.address) == contract_balance_of_rps_token + (
            amount_deposited / rps_game.getEthRpsRatio())

    contract_balance_of_rps_token = rps_token.balanceOf(rps_game.address)
    rps_game.depositFunds({"from": account, "value": amount_deposited}).wait(1)
    assert rps_game.getDepositedFundsValue(account.address) == amount_deposited * 2 / rps_game.getEthRpsRatio()
    assert rps_token.balanceOf(rps_game.address) == contract_balance_of_rps_token + (
                amount_deposited / rps_game.getEthRpsRatio())


def test_withdraw_funds_positive():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    account = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_game.depositFunds({"from":account, "value": amount_deposited}).wait(1)
    assert rps_game.getDepositedFundsValue(account.address) == amount_deposited / rps_game.getEthRpsRatio()
    # Act
    rps_game.withdrawFunds({"from": account}).wait(1)
    # Assert
    assert rps_game.getDepositedFundsValue(account.address) == 0
    assert rps_token.balanceOf(rps_game.address) == 0

def test_withdraw_with_zero_funds_fail():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    account = get_account(index=1)
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        rps_game.withdrawFunds({"from": account}).wait(1)


def test_withdraw_after_joining_game_fail():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    player_account_1 = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_game.depositFunds({"from": player_account_1, "value": amount_deposited}).wait(1)
    # Act / Assert
    rps_game.joinGame(1, 1, {'from': player_account_1})
    with pytest.raises(exceptions.VirtualMachineError):
        rps_game.withdrawFunds({"from": player_account_1}).wait(1)


def test_update_bid_values_positive():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
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


def test_update_bid_value_bad_owner_fail():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    not_owner_account = get_account(index=1)
    low_bid = rps_game.getLowBidValue()
    medium_bid = rps_game.getMediumBidValue()
    high_bid = rps_game.getHighBidValue()
    increment_value = 1
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        rps_game.updateLowBidValue(low_bid + increment_value, {"from": not_owner_account}).wait(1)
    with pytest.raises(exceptions.VirtualMachineError):
        rps_game.updateMediumBidValue(medium_bid + increment_value, {"from": not_owner_account}).wait(1)
    with pytest.raises(exceptions.VirtualMachineError):
        rps_game.updateHighBidValue(high_bid + increment_value, {"from": not_owner_account}).wait(1)

    assert low_bid == rps_game.getLowBidValue()
    assert rps_game.getLinkBidWithValues(0) == rps_game.getLowBidValue()
    assert medium_bid == rps_game.getMediumBidValue()
    assert rps_game.getLinkBidWithValues(1) == rps_game.getMediumBidValue()
    assert high_bid == rps_game.getHighBidValue()
    assert rps_game.getLinkBidWithValues(2) == rps_game.getHighBidValue()


def test_join_game_positive():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    player_account_1 = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_game.depositFunds({"from":player_account_1, "value": amount_deposited}).wait(1)
    # Act
    rps_game.joinGame(1,1, {'from': player_account_1})
    # Assert
    assert rps_game.isPlayerInQueue(player_account_1.address)


def test_join_game_no_funds_fail():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    player_account_1 = get_account(index=1)
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        rps_game.joinGame(1, 1, {'from': player_account_1})


def test_join_game_multiple_joins_fail():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    player_account_1 = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_game.depositFunds({"from": player_account_1, "value": amount_deposited}).wait(1)
    rps_game.joinGame(1, 1, {'from': player_account_1})
    # Act / Assert
    with pytest.raises(exceptions.VirtualMachineError):
        rps_game.joinGame(1, 1, {'from': player_account_1})


test_choose_winner_and_transfer_reward_data = [
    (0, 0, 0), (0, 1, 0), (0, 2, 0),
    (1, 0, 1), (1, 1, 1), (1, 2, 1),
    (2, 0, 2), (2, 1, 2), (2, 2, 2),
]

@pytest.mark.parametrize("player_1_symbol, player_2_symbol, bid_value", test_choose_winner_and_transfer_reward_data)
def test_choose_winner_and_transfer_reward(player_1_symbol, player_2_symbol, bid_value):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
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
    rps_game.joinGame(player_1_symbol, bid_value, {'from': player_account_1})
    rps_game.joinGame(player_2_symbol, bid_value, {'from': player_account_2})
    # Assert
    if (player_1_symbol == 0):
        if (player_2_symbol == 0):
            assert rps_game.getDepositedFundsValue(player_account_1.address) == player_balance_1
            assert rps_game.getDepositedFundsValue(player_account_2.address) == player_balance_2
        elif (player_2_symbol == 1):
            assert rps_game.getDepositedFundsValue(player_account_1.address) == player_balance_1 - bid_value_dict[bid_value]
            assert rps_game.getDepositedFundsValue(player_account_2.address) == player_balance_2 + bid_value_dict[bid_value]
        elif (player_2_symbol == 2):
            assert rps_game.getDepositedFundsValue(player_account_1.address) == player_balance_1 + bid_value_dict[bid_value]
            assert rps_game.getDepositedFundsValue(player_account_2.address) == player_balance_2 - bid_value_dict[bid_value]

    if (player_1_symbol == 1):
        if (player_2_symbol == 1):
            assert rps_game.getDepositedFundsValue(player_account_1.address) == player_balance_1
            assert rps_game.getDepositedFundsValue(player_account_2.address) == player_balance_2
        elif (player_2_symbol == 0):
            assert rps_game.getDepositedFundsValue(player_account_1.address) == player_balance_1 + bid_value_dict[bid_value]
            assert rps_game.getDepositedFundsValue(player_account_2.address) == player_balance_2 - bid_value_dict[bid_value]
        elif (player_2_symbol == 2):
            assert rps_game.getDepositedFundsValue(player_account_1.address) == player_balance_1 - bid_value_dict[bid_value]
            assert rps_game.getDepositedFundsValue(player_account_2.address) == player_balance_2 + bid_value_dict[bid_value]

    if (player_1_symbol == 2):
        if (player_2_symbol == 2):
            assert rps_game.getDepositedFundsValue(player_account_1.address) == player_balance_1
            assert rps_game.getDepositedFundsValue(player_account_2.address) == player_balance_2
        elif (player_2_symbol == 0):
            assert rps_game.getDepositedFundsValue(player_account_1.address) == player_balance_1 - bid_value_dict[bid_value]
            assert rps_game.getDepositedFundsValue(player_account_2.address) == player_balance_2 + bid_value_dict[bid_value]
        elif (player_2_symbol == 1):
            assert rps_game.getDepositedFundsValue(player_account_1.address) == player_balance_1 + bid_value_dict[bid_value]
            assert rps_game.getDepositedFundsValue(player_account_2.address) == player_balance_2 - bid_value_dict[bid_value]


def test_quite_queue_positive():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
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

def test_quite_queue_without_joining_game_fail():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")
    # Arrange
    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    player_account_1 = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_game.depositFunds({"from":player_account_1, "value": amount_deposited}).wait(1)
    # Act / Arrange
    with pytest.raises(exceptions.VirtualMachineError):
        rps_game.quiteQueue({"from": player_account_1})