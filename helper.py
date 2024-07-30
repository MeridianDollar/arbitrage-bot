from web3 import Web3
import json
import abis as abis
import time
from dotenv import load_dotenv
import os 

load_dotenv()
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
PUBLIC_KEY = os.getenv('PUBLIC_KEY')
WEI = 1e18
TRIGGER_THRESHOLD = 0.99

with open("./config.json", "r") as jsonFile:
    config = json.load(jsonFile) 
    
    
def check_provider(network_providers):
    for provider in network_providers:
        if network_provider := Web3(Web3.HTTPProvider(provider)):
            return network_provider
        

def config_swap_params(network, fromToken, toToken, amount):
    deadline = int(time.time())+1000
    
    if network == "telos":
        tuple_params = (
            fromToken,
            toToken, 
            PUBLIC_KEY, 
            deadline, 
            amount, 
            0, 
            0
            )
        return tuple_params
    
    
def fetch_token_account_balance(w3, token_address):
    token = w3.eth.contract(address=token_address, abi=abis.erc20())
    return token.functions.balanceOf(PUBLIC_KEY).call()