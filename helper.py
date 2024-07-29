from web3 import Web3
import json
import abis as abis
import time
from dotenv import load_dotenv
import os 

load_dotenv()
PRIVATE_KEY = os.getenv('PRIVATE_KEY')
PUBLIC_KEY = os.getenv('PUBLIC_KEY')


with open("./config.json", "r") as jsonFile:
    config = json.load(jsonFile) 
    
    
def check_provider(network_providers):
    for provider in network_providers:
        if network_provider := Web3(Web3.HTTPProvider(provider)):
            return network_provider