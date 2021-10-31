from scripts.helpful_scripts import get_account
from brownie import RPS_Game, RPS_Token, config, network

def deploy_rps_token_and_game():
    owner_acc = get_account()
    rps_token = RPS_Token.deploy({'from': owner_acc}, publish_source=config['networks'][network.show_active()]['publish_source'])
    rps_game = RPS_Game.deploy(rps_token.address, {"from": owner_acc}, publish_source=config['networks'][network.show_active()]['publish_source'])
    return rps_token, rps_game, owner_acc

def main():
    deploy_rps_token_and_game()