from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.deploy import deploy_rps_token_and_game
from brownie import network, exceptions, RPS_Game, RPS_Token, config
import pytest
from web3 import Web3


def test_create_new_tokens_for_game_positive():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")

    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    account = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_balance_before = rps_token.balanceOf(account.address)
    rps_game.depositFunds({"from": account, "value": amount_deposited}).wait(1)
    assert rps_token.balanceOf(account.address) == (amount_deposited * rps_game.getEthRpsRatio()) + rps_balance_before


def test_create_new_tokens_for_game_only_rps_game_modifier_fail():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")

    owner_acc = get_account()
    rps_token = RPS_Token.deploy({'from': owner_acc},
                                 publish_source=config['networks'][network.show_active()]['publish_source'])
    rps_game = RPS_Game.deploy(rps_token.address, {"from": owner_acc},
                               publish_source=config['networks'][network.show_active()]['publish_source'])
    player_acc = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    with pytest.raises(exceptions.VirtualMachineError):
        rps_game.depositFunds({"from": player_acc, "value": amount_deposited})


def test_burn_tokens_when_withdraw_positive():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")

    rps_token, rps_game, owner_acc = deploy_rps_token_and_game()
    account = get_account(index=1)
    amount_deposited = Web3.toWei(1, 'ether')
    rps_balance_before = rps_token.balanceOf(account.address)
    rps_game.depositFunds({"from": account, "value": amount_deposited}).wait(1)
    assert rps_token.balanceOf(account.address) == (amount_deposited * rps_game.getEthRpsRatio()) + rps_balance_before
    rps_game.withdrawFunds({"from": account}).wait(1)
    assert rps_token.balanceOf(account.address) == 0


def test_set_rps_game_address_positive():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Olny for local testing")

    owner_acc = get_account()
    rps_token = RPS_Token.deploy({'from': owner_acc},
                                 publish_source=config['networks'][network.show_active()]['publish_source'])
    rps_game = RPS_Game.deploy(rps_token.address, {"from": owner_acc},
                               publish_source=config['networks'][network.show_active()]['publish_source'])
    rps_token.setRPSGameAddress(rps_game.address, {"from": owner_acc})