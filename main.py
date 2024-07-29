from helper import *


def build_and_send_transaction(w3, contract_function):
    try:
        tx = contract_function.buildTransaction({
            "gasPrice": w3.eth.gasPrice,
            'from': PUBLIC_KEY, 
            'nonce': w3.eth.getTransactionCount(PUBLIC_KEY)
        })

        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        receipt = w3.eth.waitForTransactionReceipt(tx_hash, timeout=120)

        print("Transaction Complete: tx_hash", w3.toHex(tx_hash))
        return receipt
    except Exception as e:
        print(f"Transaction Failed: {str(e)}")
        return None
    

def swap_tokens_on_telos(network, w3, tx_params):
    swap_router_address = config[network]["contracts"]["swap_router"]
    swap_router_abi = abis.swapsicle_router()
    swap_router = w3.eth.contract(address=swap_router_address, abi=swap_router_abi)
    
    contract_function = swap_router.functions.exactInputSingle(tx_params)
    build_and_send_transaction(w3, contract_function, tx_params)


def redeem_collateral(network, w3, tx_params):
    trove_manager_address = config[network]["contracts"]["trove_manager"]
    trove_manager_abi = abis.trove_manager()
    trove_manager = w3.eth.contract(address=trove_manager_address, abi=trove_manager_abi)

    contract_function = trove_manager.functions.redeemCollateral(tx_params)
    build_and_send_transaction(w3, contract_function, tx_params)


def fetch_first_redemption_hint(network, w3):
    sorted_troves = w3.eth.contract(address=config[network]["contracts"]["sorted_troves"], abi=abis.sorted_troves())
    return sorted_troves.functions.getLast().call()


def fetch_previous_redemption_hint(network, w3, address):
    sorted_troves = w3.eth.contract(address=config[network]["contracts"]["sorted_troves"], abi=abis.sorted_troves())
    return sorted_troves.functions.getPrev(address).call()


def fetch_previous_redemption_hint(network, w3, address):
    sorted_troves = w3.eth.contract(address=config[network]["contracts"]["sorted_troves"], abi=abis.sorted_troves())
    return sorted_troves.functions.getPrev(address).call()


def fetch_oracle_price(network, w3):
    price_feed = w3.eth.contract(address=config[network]["contracts"]["price_feed"], abi=abis.price_feed())
    return price_feed.functions.fetchPrice().call()


def fetch_redemption_hints(network, w3, _USDMamount, _price, _maxIterations):
    hint_helpers = w3.eth.contract(address=config[network]["contracts"]["hint_helpers"], abi=abis.hint_helpers())
    return hint_helpers.functions.getRedemptionHints(_USDMamount, _price, _maxIterations).call()


def fetch_redemption_fee_wit_decay(network, w3, _USDMamount):
    trove_manager = w3.eth.contract(address=config[network]["contracts"]["trove_manager"], abi=abis.trove_manager())
    return trove_manager.functions.getRedemptionFeeWithDecay(_USDMamount).call()  


def quote_exact_input_single(network, w3, fee, amount_in):
    quoter = w3.eth.contract(address=config[network]["contracts"]["quoter"], abi=abis.quoter())
    return quoter.functions.quoteExactInputSingle(
        config[network]["tokens"]["collateral"],
        config[network]["tokens"]["USDT"],
        amount_in,
        0).call()  


def configure_redemption_params(network, w3):
    _maxIterations = 70
    _USDMamount = int(10e18)
    
    _maxFeePercentage = fetch_redemption_fee_wit_decay(network, w3, _USDMamount)
    
    _collateralPrice = fetch_oracle_price(network, w3)
    
    amountOfCollateral = _USDMamount / _collateralPrice

    fees = amountOfCollateral * _maxFeePercentage *1e-19
    collateralRecieved = amountOfCollateral - fees
    
    print(collateralRecieved, "Collateral received")
    
    
    _firstRedemptionHint, _partialRedemptionHintNICR, truncatedLUSDamount = fetch_redemption_hints( network, w3, _USDMamount, _collateralPrice, _maxIterations)
    _upperPartialRedemptionHint = fetch_previous_redemption_hint(network, w3, _firstRedemptionHint)
    _lowerPartialRedemptionHint = _firstRedemptionHint
    
    params = [_USDMamount, 
              _firstRedemptionHint, 
              _upperPartialRedemptionHint,
              _lowerPartialRedemptionHint,
              _partialRedemptionHintNICR,
              _maxIterations,
              _maxFeePercentage]
    
    return params
    
network = "telos"
w3 = check_provider(config[network]["rpcs"])

# configure_redemption_params(network, w3)



amount_out = quote_exact_input_single(network, w3, 0, int(10e18))
print(amount_out)