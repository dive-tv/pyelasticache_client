from pymemcache.client.autodiscovery import AutodiscoveryClient
from .test_client import MockSocket

import unittest
import pytest

class MockSocketModule(object):

    def __init__(self, recv_bufs):
        self.sock = MockSocket(recv_bufs)
        self.AF_INET = 0
        self.SOCK_STREAM = 0
    
    def socket(self, family, type):
        return self.sock

    #def __getattr__(self, name):
    #    return getattr(socket, name)
        
@pytest.mark.unit()
class TestAutodiscoveryClient(unittest.TestCase):
        
    def make_client(self, mock_socket_values, **kwargs):
        
        kwargs.update({
            'socket_module': MockSocketModule(list(mock_socket_values))
        })
        client = AutodiscoveryClient(endpoint=("127.0.0.1", 11211), autodiscovery=False, **kwargs)
        
        return client
        

    def test_cluster_one_node(self):
        # autodiscovery returns one node
        ###########
        
        client = self.make_client([
            b'VERSION 1.4.20\r\n', 
            b'CONFIG cluster 0 147\r\n1\nlocalhost|127.0.0.1|11211\n\r\nEND\r\n'
        ])
        
        assert len(client.clients) == 1
        assert client.clients['127.0.0.1:11211'] is not None

    def test_cluster_two_nodes(self):
        # autodiscovery returns two nodes
        ###########
        
        client = self.make_client([
            b'VERSION 1.4.20\r\n', 
            b'CONFIG cluster 0 147\r\n1\nlocalhost|127.0.0.1|11211 localhost|127.0.0.1|11212\n\r\nEND\r\n'
        ])
        
        assert len(client.clients) == 2
        assert client.clients['127.0.0.1:11211'] is not None
        assert client.clients['127.0.0.1:11212'] is not None
        
    def test_cluster_no_changes(self):
        # autodiscovery returns one node and then the same
        ###########
        
        client = self.make_client([
            b'VERSION 1.4.20\r\n', 
            b'CONFIG cluster 0 147\r\n1\nlocalhost|127.0.0.1|11211\n\r\nEND\r\n',
            b'VERSION 1.4.20\r\n',
            b'CONFIG cluster 0 147\r\n1\nlocalhost|127.0.0.1|11211\n\r\nEND\r\n',
        ])
        
        assert len(client.clients) == 1
        assert client.clients['127.0.0.1:11211'] is not None
        
        client.check_cluster()
        
        assert len(client.clients) == 1
        assert client.clients['127.0.0.1:11211'] is not None
        
    def test_cluster_add_node(self):
        # autodiscovery returns one and then two nodes
        ###########
        
        client = self.make_client([
            b'VERSION 1.4.20\r\n', 
            b'CONFIG cluster 0 147\r\n1\nlocalhost|127.0.0.1|11211\n\r\nEND\r\n',
            b'VERSION 1.4.20\r\n',
            b'CONFIG cluster 0 147\r\n2\nlocalhost|127.0.0.1|11211 localhost|127.0.0.1|11212\n\r\nEND\r\n'
        ])
        
        assert len(client.clients) == 1
        assert client.clients['127.0.0.1:11211'] is not None
        
        client.check_cluster()
        
        assert len(client.clients) == 2
        assert client.clients['127.0.0.1:11211'] is not None
        assert client.clients['127.0.0.1:11212'] is not None
        
    def test_cluster_remove_node(self):
        # autodiscovery returns two and then one nodes
        ###########
        
        client = self.make_client([
            b'VERSION 1.4.20\r\n', 
            b'CONFIG cluster 0 147\r\n1\nlocalhost|127.0.0.1|11211 localhost|127.0.0.1|11212\n\r\nEND\r\n',
            b'VERSION 1.4.20\r\n',
            b'CONFIG cluster 0 147\r\n2\nlocalhost|127.0.0.1|11211\n\r\nEND\r\n'
        ])
        
        assert len(client.clients) == 2
        assert client.clients['127.0.0.1:11211'] is not None
        assert client.clients['127.0.0.1:11212'] is not None
        
        client.check_cluster()
        
        assert len(client.clients) == 1
        assert client.clients['127.0.0.1:11211'] is not None
        
    def test_cluster_key_add_node(self):
        # test key consistency after adding nodes
        ###########
        
        client = self.make_client([
            b'VERSION 1.4.20\r\n', 
            b'CONFIG cluster 0 147\r\n1\nlocalhost|127.0.0.1|11211\n\r\nEND\r\n',
            b'VERSION 1.4.20\r\n',
            b'CONFIG cluster 0 147\r\n2\nlocalhost|127.0.0.1|11211 localhost|127.0.0.1|11212\n\r\nEND\r\n'
        ])
        
        assert client.hasher.get_node("b") == client.hasher.get_node("z")
        
        client.check_cluster()
        
        assert client.hasher.get_node("b") != client.hasher.get_node("z")
        
    def test_cluster_key_remove_node(self):
        # test key consistency after removing nodes
        ###########
        
        client = self.make_client([
            b'VERSION 1.4.20\r\n', 
            b'CONFIG cluster 0 147\r\n1\nlocalhost|127.0.0.1|11211 localhost|127.0.0.1|11212\n\r\nEND\r\n',
            b'VERSION 1.4.20\r\n',
            b'CONFIG cluster 0 147\r\n2\nlocalhost|127.0.0.1|11211\n\r\nEND\r\n'
        ])
        
        assert client.hasher.get_node("b") != client.hasher.get_node("z")
        
        client.check_cluster()
        
        assert client.hasher.get_node("b") == client.hasher.get_node("z")