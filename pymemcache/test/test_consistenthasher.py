import sys

from pymemcache.client.consistenthasher import ConsistentHash

import unittest
import pytest

NUM_KEYS = 10
NUM_RESULTS = 5

class TestConsistentHasher(unittest.TestCase):

        
    def hash_keys(self, hasher):

        res = []
        for key in range(ord('a'), ord('a') + NUM_KEYS):
            res.append(hasher.get_node(chr(key)))
        return res


    def test_empty_nodes(self):
        # no nodes
        ###########
        
        hasher = ConsistentHash()
        res = self.hash_keys(hasher)

        # all keys return None
        for i in range(0, NUM_RESULTS):
            assert res[i] is None


    def test_add_10_nodes(self):
        # add 10 nodes
        ###########
        
        hasher = ConsistentHash()
        for i in range(1,11):
            node = '172.31.0.%i' % i + ':3000'
            hasher.add_node(node)

        res = self.hash_keys(hasher)
        
        # no keys return None
        for i in range(0, NUM_RESULTS):
            assert res[i] is not None
        
        
    def test_remove_first_5_nodes(self):
        # remove first 5 nodes
        ###########
        
        hasher = ConsistentHash()
        
        for i in range(1,11):
            node = '172.31.0.%i' % i + ':3000'
            hasher.add_node(node)
            
        res1 = self.hash_keys(hasher)
        
        for i in range(1,6):
            node = '172.31.0.%i' % i + ':3000'
            hasher.remove_node(node)

        res2 = self.hash_keys(hasher)

        # keys on deleted nodes change assigned node
        # keys on kept nodes keep same node
        for i in range(0, NUM_RESULTS):
            init_node = int(res1[i][9:10])
            curr_node = int(res2[i][9:10])
            if init_node in range(1,6):
                assert init_node != curr_node
            elif init_node in range(6,11):
                assert init_node == curr_node
        
        
    def test_add_first_5_nodes(self):
        # add removed nodes again
        ###########
        
        hasher = ConsistentHash()
        
        for i in range(1,11):
            node = '172.31.0.%i' % i + ':3000'
            hasher.add_node(node)
            
        res1 = self.hash_keys(hasher)
        
        for i in range(1,6):
            node = '172.31.0.%i' % i + ':3000'
            hasher.remove_node(node)
        for i in range(1,6):
            node = '172.31.0.%i' % i + ':3000'
            hasher.add_node(node)

        res2 = self.hash_keys(hasher)

        # all keys go back to initial node assignments
        for i in range(0, NUM_RESULTS):
            init_node = int(res1[i][9:10])
            curr_node = int(res2[i][9:10])
            assert init_node == curr_node
              
                
    def test_remove_last_5_nodes(self):
        # remove last 5 nodes
        ###########
        
        hasher = ConsistentHash()
        
        for i in range(1,11):
            node = '172.31.0.%i' % i + ':3000'
            hasher.add_node(node)
            
        res1 = self.hash_keys(hasher)
        
        for i in range(6,11):
            node = '172.31.0.%i' % i + ':3000'
            hasher.remove_node(node)

        res2 = self.hash_keys(hasher)

        # keys on deleted nodes change assigned node
        # keys on kept nodes keep same node
        for i in range(0, NUM_RESULTS):
            init_node = int(res1[i][9:10])
            curr_node = int(res2[i][9:10])
            if init_node in range(1,6):
                assert init_node == curr_node
            elif init_node in range(6,11):
                assert init_node != curr_node
                