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


class AutodiscoveryClient(object):
    """
    A hashed client implementing memcached cluster autodiscovery feature
    """
    def __init__(
        self,
        endpoint,
        interval=60,
        hasher=ConsistentHash,
        *args,
        **kwargs
    ):
        """
        Constructor.

        Args:
          cluster_endpoint: tuple(hostname, port)
          autodiscovery_interval: seconds to check for updates on cluster nodes
          hasher: object implementing functions ``get_node``, ``add_node``,
                  and ``remove_node``

        Further arguments are interpreted as for :py:class:`.Client`
        constructor.
        """
        
        # connect to endpoint
        self.endpoint = Client(server=endpoint, *args, **kwargs)
        self.interval = interval
        
        # load current cluster version and nodes
        (self.cluster_version, self.nodes) = self.get_cluster_nodes()
        
        logger.debug('Cluster version: %s', self.cluster_version)
        logger.debug('Initial cluster nodes: %s',  self.nodes)
        
        self.client = HashClient(servers=self.nodes, hasher=hasher, *args, **kwargs)
        
        # start autodiscovery interval
        self.check_cluster(False)
        
        
    def get_cluster_nodes(self):
    
        cluster_info = None
    
        # check memcached version and obtain cluster info
        mc_version = self.endpoint.version()
        if StrictVersion(mc_version) >= StrictVersion('1.4.14'):
            cluster_info = self.endpoint.config('cluster')
        else:
            cluster_info = self.endpoint.get('AmazonElastiCache:cluster')
        
        # parse cluster version and nodes
        splitter = re.compile(r'\r?\n')
        cluster = splitter.split(cluster_info)
        
        cluster_version = cluster[1]
        node_list = cluster[2].split(' ')
        servers = []
        for node in node_list:
            info = node.split('|')
            if len(info) == 3:
                servers.append((info[1], info[2]))
                
        return (cluster_version, servers)
        
        
    def check_cluster(self, do_check=True):
    
        threading.Timer(self.interval, self.check_cluster).start()
        
        if do_check:
        
            logger.debug('Checking cluster nodes..')
            
            (version, nodes) = self.get_cluster_nodes()
            if version != self.cluster_version:
                
                logger.debug('Cluster version changed from %s to %s. Reloading nodes..',  
                            version, self.cluster_version)
                
                self.cluster_version = version
                
                # check removed nodes
                for node in self.nodes:
                    if not node in nodes:
                        logger.debug('Removing node from cluster: %s',  node)
                        self.client.remove_server(node[0], node[1])
                
                # check new nodes
                for node in nodes:
                    if not node in self.nodes:
                        logger.debug('Adding node to cluster: %s',  node)
                        self.client.add_server(node[0], node[1])
                        
                self.nodes = nodes