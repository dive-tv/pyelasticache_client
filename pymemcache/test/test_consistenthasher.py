import sys

sys.path.append('../client')

from consistenthasher import ConsistentHash

#from pymemcache.client.consistenthasher import ConsistentHash
#from pymemcache.client.hash import HashClient

NUM_KEYS = 10
NUM_RESULTS = 5

def test_hasher():

    print(len(hasher.get_nodes()))
    
    res = []
    for key in range(ord('a'), ord('a') + NUM_KEYS):
        res.append(hasher.get_node(chr(key)))
    return res


#client = HashClient(servers = [('172.31.0.1', 3000), ('172.31.0.2', 3000)],
#         hasher = ConsistentHash())
         
hasher = ConsistentHash()
results = []

results.append(test_hasher())

for i in range(1,11):
    node = '172.31.0.%i' % i + ':3000'
    hasher.add_node(node)

results.append(test_hasher())
    
for i in range(1,6):
    node = '172.31.0.%i' % i + ':3000'
    hasher.remove_node(node)

results.append(test_hasher())

for i in range(1,6):
    node = '172.31.0.%i' % i + ':3000'
    hasher.add_node(node)

results.append(test_hasher())

for i in range(6,11):
    node = '172.31.0.%i' % i + ':3000'
    hasher.remove_node(node)

results.append(test_hasher())

for test in range(0, NUM_RESULTS):
    print (results[test])
