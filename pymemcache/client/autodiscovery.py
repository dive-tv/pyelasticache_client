import socket
import time
import logging

from pymemcache.client.base import Client
from pymemcache.client.hash import HashClient
from pymemcache.client.consistenthasher import ConsistentHash

import re
from distutils.version import StrictVersion
import threading

logger = logging.getLogger(__name__)


class AutodiscoveryClient(HashClient):
    """
    A hashed client implementing memcached cluster autodiscovery feature
    """
    def __init__(
        self,
        endpoint,
        autodiscovery=True,
        interval=60,
        hasher=ConsistentHash,
        *args,
        **kwargs
    ):
        """
        Constructor.

        Args:
          cluster_endpoint: tuple(hostname, port)
          autodiscovery: activates / deactivates automatic cluster node update
          interval: seconds to check for updates on cluster nodes, if autodiscovery is True
          hasher: object implementing functions ``get_node``, ``add_node``,
                  and ``remove_node``

        Further arguments are interpreted as for :py:class:`.HashClient`
        constructor.
        """
        
        # create cluster client
        super(AutodiscoveryClient, self).__init__(servers=[], hasher=hasher, *args, **kwargs)
        
        # init cluster params
        self.endpoint = endpoint
        self.cluster_version = 0
        self.autodiscovery = autodiscovery
        self.interval = interval
        
        # start autodiscovery thread
        self.check_cluster()
        
        
    def get_cluster_nodes(self):
    
        # connect to mgmt node
        # this connection is not kept, as DNS resolution might point to another node
        mgmt = Client(server=self.endpoint)
        
        # check memcached version and obtain cluster info
        cluster_info = None
        memcached_version = mgmt.version()
        if StrictVersion(memcached_version) >= StrictVersion('1.4.14'):
            cluster_info = mgmt.config('cluster')
        else:
            cluster_info = mgmt.get('AmazonElastiCache:cluster')
        
        # parse cluster version and nodes
        splitter = re.compile(r'\r?\n')
        cluster = splitter.split(cluster_info)
        
        cluster_version = int(cluster[1])
        node_list = cluster[2].split(' ')
        servers = []
        for node in node_list:
            info = node.split('|')
            if len(info) == 3:
                servers.append((info[1], info[2]))
                
        return (cluster_version, servers)
        
        
    def check_cluster(self):
    
        if self.autodiscovery:
            threading.Timer(self.interval, self.check_cluster).start()
        
        print('Checking cluster nodes..')
        
        (new_version, new_nodes) = self.get_cluster_nodes()
        if new_version != self.cluster_version:
            
            print('Cluster version changed from %i to %i. Reloading nodes..',  
                        self.cluster_version, new_version)
            self.cluster_version = new_version
            
            # check removed nodes
            for node in self.clients.keys():
                if not node in new_nodes:
                    print('Removing node from cluster: %s',  node)
                    self.remove_server(node[0], node[1])
            
            # check new nodes
            for node in new_nodes:
                if not node in self.clients.keys():
                    print('Adding node to cluster: %s',  node)
                    self.add_server(node[0], node[1])
