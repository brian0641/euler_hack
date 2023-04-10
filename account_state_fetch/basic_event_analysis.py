import json, pickle
from pprint import pprint

f = open("all_events.log", 'r') 
events = []
for line in f:
    d = json.loads(line)
    events.append(d)            
f.close()


print("Number of read events:", len(events))

event_types = set([d['event'] for d in events])
print(event_types)

block_numbers = [d['blockNumber'] for d in events]
print(f"min block nunber is {min(block_numbers)} and max block nunber is {max(block_numbers)}")

arg_addresses = set([d['args']['account'] for d in events])

print(f'  Num account addresses: {len(arg_addresses)}. ')

token_info = pickle.load( open( "token_info.pickle", "rb" ) )
pprint(token_info)