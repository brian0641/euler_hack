"""

Build a list of addresses relevant to the protocol by fetching Deposit, Withdraw, Borrow, 
Repay events from euler.sol

"""

import Ethereum.EventTracker as EventTracker
import web3, json, pprint, time, requests

def convertEvent(obj):
    """ 
    Gets rid of AttibuteDict and HexBytes from an event object
    """
    o = dict(obj)
    o['args'] = dict(o['args'])
    o['blockHash'] = o['blockHash'].hex()
    o['transactionHash'] = o['transactionHash'].hex()
    return o

def fetchEvents(str_event, first_block, max_block, euler_k, et, w3):
    """
    Fetch Events
    """
    start_block = first_block
    window_size = 5000
    
    print(f'Begin fetching events for event: {str_event}. Start block: {start_block}')
    euler_k_events = eval("euler_k.events." + str_event)
    while start_block <= max_block:
        try:
            l = et.fetchEventsBlockRange(euler_k_events, start_block, start_block + window_size)
        except requests.exceptions.ReadTimeout:
            print("READ TIMEOUT")
            time.sleep(30)
            window_size = max(50, window_size - 100)
            continue
        except:
            print("error")
            break
        if l:
            d =  convertEvent(l[-1])
           
        print(f'Number of {str_event} events fetched: {len(l)}. Start block = {start_block}; end block = {start_block + window_size}')
        start_block += window_size
        start_block = min(start_block, max_block + 1)
        
        window_size = min(window_size + 100, 5000)
        
        time.sleep(0.1)
        
        if l:
            f = open("all_events.log", 'a')
            for o in l:
                d =  convertEvent(o)
                f.write(json.dumps(d) + '\n') 
            f.close()            
            
"""
MAIN
"""

EULER_K_ADDRESS = "0x27182842E098f60e3D576794A5bFFb0777E025d3"
EVENTS = ["Deposit", "Withdraw", "Borrow", "Repay"]
MIN_BLOCK = 13500000
MAX_BLOCK = 17000000

provider_url = "http://10.67.152.102:8545"
abi = json.load(open("./abis/euler_abi.json", "r"))

provider = web3.Web3.HTTPProvider(provider_url)
w3 = web3.Web3(provider)        
    
et = EventTracker.EventTracker(provider_url, 1)
euler_k = w3.eth.contract(address = EULER_K_ADDRESS, abi = abi) 

for str_event in EVENTS:
    events_keys = fetchEvents(str_event, MIN_BLOCK, MAX_BLOCK, euler_k, et, w3)
        
        





       



