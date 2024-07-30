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
    

def wrap_tokens(network, w3, value):
    try:
        _weth_contract = w3.eth.contract(address=config[network]["tokens"]["collateral"], abi=abis.wrapped_tokens())

        tx = _weth_contract.functions.deposit().buildTransaction({
            "gasPrice": w3.eth.gasPrice,
            'value': value,
            'from': PUBLIC_KEY, 
            'nonce': w3.eth.getTransactionCount(PUBLIC_KEY)
        })  
        
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        w3.eth.waitForTransactionReceipt(tx_hash, timeout=120)

        print("Wrap Tokens  Complete : tx_hash", w3.toHex(tx_hash))
        return value
           
    except Exception as e:
        print(e,"Wrap Tokens Failed")
        
        
def swap_tokens_on_telos(network, w3, tx_params):
    swap_router_address = config[network]["contracts"]["swap_router"]
    swap_router_abi = abis.swapsicle_router()
    swap_router = w3.eth.contract(address=swap_router_address, abi=swap_router_abi)
    
    contract_function = swap_router.functions.exactInputSingle(tx_params)
    build_and_send_transaction(w3, contract_function)


def redeem_collateral(network, w3, tx_params):
    trove_manager_address = config[network]["contracts"]["trove_manager"]
    trove_manager_abi = abis.trove_manager()
    trove_manager = w3.eth.contract(address=trove_manager_address, abi=trove_manager_abi)

    contract_function = trove_manager.functions.redeemCollateral(
        tx_params[0],
        tx_params[1],
        tx_params[2],
        tx_params[3],
        tx_params[4],
        tx_params[5],
        tx_params[6]
        )
    build_and_send_transaction(w3, contract_function)


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


def quote_exact_input_single(network, w3, amount_in, token_in, token_out):
    quoter = w3.eth.contract(address=config[network]["contracts"]["quoter"], abi=abis.quoter())
    tokens_out = quoter.functions.quoteExactInputSingle(
        token_in,
        token_out,
        amount_in,
        0).call() 
    return tokens_out[0]


def configure_redemption_params(network, w3, _USDMamount):
    
    _maxIterations = 70
    _maxFeePercentage = fetch_redemption_fee_wit_decay(network, w3, _USDMamount)
    _collateralPrice = fetch_oracle_price(network, w3)
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
    

def quote_amount_out_redemptions(usdm_amount):
    _maxFeePercentage = fetch_redemption_fee_wit_decay(network, w3, usdm_amount)
    _collateralPrice = fetch_oracle_price(network, w3)
    
    amountOfCollateral = usdm_amount / _collateralPrice
    fees = amountOfCollateral * _maxFeePercentage *1e-19
    collateralRecieved = amountOfCollateral - fees

    return collateralRecieved * WEI


def check_for_arbitrage(network, w3, amount_in):
    collateral = config[network]["tokens"]["collateral"]
    usdc = config[network]["tokens"]["USDC"]
    usdm = config[network]["tokens"]["USDM"]

    usdm_for_usdc = quote_exact_input_single(network, w3, amount_in, usdc, usdm)
    collateral_for_usdm = quote_amount_out_redemptions(usdm_for_usdc)
    usdc_for_collateral = quote_exact_input_single(network, w3, int(collateral_for_usdm), collateral, usdc)
    
    print(usdc_for_collateral, "usdc_for_collateral")

    if (usdc_for_collateral * TRIGGER_THRESHOLD) > amount_in:
        if network =="telos":
            swap_params = config_swap_params(network, usdc, usdm, amount_in)  
            swap_tokens_on_telos(network, w3, swap_params)
            
            usdm_balance = fetch_token_account_balance(w3, usdm)   
            collateral_out = quote_amount_out_redemptions(usdm_balance) 
                 
            redemption_params = configure_redemption_params(network, w3, usdm_balance)
            redeem_collateral(network, w3, redemption_params)
            
            value = wrap_tokens(network, w3, int(collateral_out)) 
            swap_params = config_swap_params(network, collateral, usdc, value)  
            swap_tokens_on_telos(network, w3, swap_params)
    else:
        print("No arbitrage oppertunity available")



network = "telos"
w3 = check_provider(config[network]["rpcs"])
amount_in = int(50e6)      

check_for_arbitrage(network, w3, amount_in)
