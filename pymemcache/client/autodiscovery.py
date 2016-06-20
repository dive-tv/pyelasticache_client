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
        self.args = args
        self.kwargs = kwargs
        self.cluster_version = 0
        self.autodiscovery = autodiscovery
        self.interval = interval
        self.timer = None

        # start autodiscovery thread
        self.check_cluster()
        
        
    def get_cluster_nodes(self):
    
        # connect to mgmt node
        # this connection is not kept, as DNS resolution might point to another node
        mgmt = Client(server=self.endpoint, *self.args, **self.kwargs)
        
        # check memcached version and obtain cluster info
        cluster_info = None
        memcached_version = mgmt.version().decode()
        
        if StrictVersion(memcached_version) >= StrictVersion('1.4.14'):
            cluster_info = mgmt.config(b'cluster').decode()
        else:
            cluster_info = mgmt.get(b'AmazonElastiCache:cluster').decode()
        
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
    
        logger.debug('Checking cluster nodes..')
        
        (new_version, new_nodes) = self.get_cluster_nodes()
        if new_version != self.cluster_version:
            
            logger.info('Cluster version changed from %i to %i. Reloading nodes..',  
                        self.cluster_version, new_version)
            self.cluster_version = new_version
            
            # check removed nodes
            deleted_nodes = []
            for node in self.clients.keys():
                ip_port = node.split(":")
                if len(ip_port) == 2 and not (ip_port[0], ip_port[1]) in new_nodes:
                    logger.info('Removing node from cluster: %s',  node)
                    deleted_nodes.append(node)
                    self.remove_server(ip_port[0], int(ip_port[1]))
            
            # update client nodes
            for node in deleted_nodes:
                del self.clients[node]
            
            # check new nodes
            for node in new_nodes:
                node_str = node[0] + ":" + node[1]
                if not node_str in self.clients.keys():
                    logger.info('Adding node to cluster: %s',  node)
                    self.add_server(node[0], int(node[1]))

        if self.autodiscovery:
            self.timer = threading.Timer(self.interval, self.check_cluster)
            self.timer.start()
        
    
    def close(self):

        if self.autodiscovery and self.timer is not None:
            self.timer.cancel()
            self.timer = None
            self.autodiscovery = False
            logger.info('Autodiscovery thread stopped')
