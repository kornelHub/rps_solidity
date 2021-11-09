from scripts.helpful_scripts import get_account
from brownie import RPS_Game, RPS_Token, config, network

def deploy_rps_token_and_game():
    owner_acc = get_account()
    rps_token = RPS_Token.deploy({'from': owner_acc},
                                 publish_source=config['networks']
                                 [network.show_active()]
                                 ['publish_source'])
    rps_game = RPS_Game.deploy(rps_token.address,
                               {"from": owner_acc},
                               publish_source=config['networks']
                               [network.show_active()]
                               ['publish_source'])
    rps_token.setRPSGameAddress(rps_game.address, {'from': owner_acc}).wait(1)
    return rps_token, rps_game, owner_acc

def generate_flattern_contrac():
    f = open("./rps_token.txt", 'w')
    f.write(RPS_Token.get_verification_info()["flattened_source"])
    f.close()

    f2 = open("./rps_game.txt", 'w')
    f2.write(RPS_Game.get_verification_info()["flattened_source"])
    f2.close()

def main():
    deploy_rps_token_and_game()