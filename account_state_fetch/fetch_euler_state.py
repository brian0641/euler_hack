import web3, json, math
from pprint import pprint
import pickle

contracts = {
    "euler": "0x27182842E098f60e3D576794A5bFFb0777E025d3",
    "markets": "0x3520d5a913427E6F0D6A83E07ccD4A4da316e4d3",
    "liquidation": "0xf43ce1d09050BAfd6980dD43Cde2aB9F18C85b34",
    "exec": "0x59828FdF7ee634AaaD3f58B19fDBa3b03E2D9d80"
}

LAST_BLOCK = 16818362


def fetchTokenInfo(tok_k):
    """Returns a dictionary incluing the descriptive information for a erc20 token.
    
    Args:
      tok_k (web3 contract) The erc20 token contract.

    Returns:
      dict: dict with the fields name, symbol, decimals, mantissa
    """
    decimals = tok_k.functions.decimals().call()
    
    try:
        name = tok_k.functions.name().call()
    except:
        name = "unknown"
    
    try:
        symbol = tok_k.functions.symbol().call()
    except:
        symbol = "unknown"

    d = {'name': name, 'symbol': symbol, 'decimals': decimals, 
         'mantissa': math.pow(10, decimals)}
    return d

def readAccounts():
    f = open("all_events.log", 'r') 
    events = []
    for line in f:
        d = json.loads(line)
        events.append(d)            
    f.close()
    all_accounts = set([d['args']['account'] for d in events])       
    return all_accounts


if __name__ == "__main__":
    all_accounts = readAccounts()
    
    provider_url = ""    #provider url, must be archive node. quicknode has reasonable prices
    provider = web3.Web3.HTTPProvider(provider_url)
    w3 = web3.Web3(provider) 

    token_info = {}  #erc20 token address => token_info dict
    etokens = {}  # market => etoken address
    dtokens = {}  # market => dtoken address  
    
    try:
        token_info = pickle.load( open( "token_info.pickle", "rb" ) )
    except:
        token_info = {}
    
    erc20_abi = json.load(open("./abis/erc20_abi.json", "r"))
    etoken_abi= json.load(open("./abis/etoken_abi.json", "r"))
    markets_abi= json.load(open("./abis/markets_abi.json", "r"))
    
    # dict of contract_label => abi    
    k_markets = w3.eth.contract(address = contracts['markets'],abi= markets_abi)    
    
    for i, wallet in enumerate(all_accounts):
        print(f"{i}: Fetching balances for account: {wallet}")
        
        #list of entered markets for the address
        entered_markets = k_markets.functions.getEnteredMarkets(wallet).call(block_identifier= LAST_BLOCK)    
        
        # dict of market_addr => token info
        for addr in entered_markets:
            if not addr in token_info: 
                k =  w3.eth.contract(address = addr, abi= erc20_abi )  
                token_info[addr] = fetchTokenInfo(k)    
                pickle.dump(token_info, open( "token_info.pickle", "wb" ) )  #save to disk cache
            
        for addr in entered_markets:
            if not addr in etokens:
                etoken_addr = k_markets.functions.underlyingToEToken(addr).call(block_identifier= LAST_BLOCK)
                k = w3.eth.contract(address = etoken_addr, abi= etoken_abi) 
                etokens[addr] = (etoken_addr, k)
            if not addr in dtokens:
                dtoken_addr = k_markets.functions.underlyingToDToken(addr).call(block_identifier= LAST_BLOCK)
                k = w3.eth.contract(address = dtoken_addr, abi= etoken_abi ) 
                dtokens[addr] = (dtoken_addr, k)
        
        #lookup underlying balance for each etoken
        underlying_balances_deposits = {}
        for entered_mkt_addr, tup in etokens.items():
            etoken_addr, k = tup
            b = k.functions.balanceOfUnderlying(wallet).call(block_identifier= LAST_BLOCK) 
            if b > 0:
                underlying_balances_deposits[token_info[entered_mkt_addr]['symbol']] = b / token_info[entered_mkt_addr]['mantissa']
                
        #lookup underlying balances for each dtoken
        underlying_balances_borrows = {}
        for entered_mkt_addr, tup in dtokens.items():
            dtoken_addr, k = tup
            b = k.functions.balanceOf(wallet).call(block_identifier= LAST_BLOCK)  #debt owed
            if b > 0:
                underlying_balances_borrows[token_info[entered_mkt_addr]['symbol']] = b / token_info[entered_mkt_addr]['mantissa']
                
        print("Wallet: ", wallet)
        pprint(underlying_balances_deposits)
        pprint(underlying_balances_borrows)
        #if underlying_balances_borrows or underlying_balances_deposits:
            #o = {wallet: {"borrows": underlying_balances_borrows, 
                          #"deposits": underlying_balances_deposits}
                #}
            #f = open("all_accounts.log", 'a')
            #f.write(json.dumps(o) + '\n') 
            #f.close()        
            
            

   
