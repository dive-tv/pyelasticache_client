import sys

from pymemcache.client.consistenthasher import ConsistentHash

NUM_KEYS = 10
NUM_RESULTS = 5

def hash_keys(hasher):

    print(len(hasher.get_nodes()))
    
    res = []
    for key in range(ord('a'), ord('a') + NUM_KEYS):
        res.append(hasher.get_node(chr(key)))
    return res


def test():
            
    hasher = ConsistentHash()
    results = []

    # no nodes
    ###########
    
    results.append(hash_keys(hasher))

    # all keys return None
    for i in range(0, NUM_RESULTS):
        assert results[0][i] is None

    # add 10 nodes
    ###########
    
    for i in range(1,11):
        node = '172.31.0.%i' % i + ':3000'
        hasher.add_node(node)

    results.append(hash_keys(hasher))

    # no keys return None
    for i in range(0, NUM_RESULTS):
        assert results[1][i] is not None
    
    # remove first 5 nodes
    ###########
    
    for i in range(1,6):
        node = '172.31.0.%i' % i + ':3000'
        hasher.remove_node(node)

    results.append(hash_keys(hasher))

    # keys on deleted nodes change assigned node
    # keys on kept nodes keep same node
    for i in range(0, NUM_RESULTS):
        init_node = int(results[1][i][9:10])
        curr_node = int(results[2][i][9:10])
        if init_node in range(1,6):
            assert init_node != curr_node
        elif init_node in range(6,11):
            assert init_node == curr_node
    
    # add removed nodes again
    ###########
    
    for i in range(1,6):
        node = '172.31.0.%i' % i + ':3000'
        hasher.add_node(node)

    results.append(hash_keys(hasher))

    # all keys go back to initial node assignments
    for i in range(0, NUM_RESULTS):
        init_node = int(results[1][i][9:10])
        curr_node = int(results[3][i][9:10])
        assert init_node == curr_node
            
    
    # remove last 5 nodes
    ###########
    
    for i in range(6,11):
        node = '172.31.0.%i' % i + ':3000'
        hasher.remove_node(node)

    results.append(hash_keys(hasher))

    # keys on deleted nodes change assigned node
    # keys on kept nodes keep same node
    for i in range(0, NUM_RESULTS):
        init_node = int(results[1][i][9:10])
        curr_node = int(results[4][i][9:10])
        if init_node in range(1,6):
            assert init_node == curr_node
        elif init_node in range(6,11):
            assert init_node != curr_node
    
    for test in range(0, NUM_RESULTS):
        print (results[test])


if __name__ == '__main__':
    test()