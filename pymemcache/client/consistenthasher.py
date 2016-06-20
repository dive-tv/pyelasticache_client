import sys

from pymemcache.client.ketama import ketama
from sortedcontainers import SortedDict

class ConsistentHash(object):
    """
        Implements the AWS Autodiscovery feature, using Ketama hash to
        locate cache nodes.

        Maintains an updated list of cluster nodes.
    """
    def __init__(self, nodes=None, seed=0, hash_function=ketama, reps=160):
        """
        Constructor.
        """
        self.nodes = []
        if nodes is not None:
            self.nodes = nodes
        self.hash_function = hash_function
        #self.seed = seed
        self.reps = reps
        self.update_continuum()
        
    def add_node(self, node):
        if node not in self.nodes:
            self.nodes.append(node)
            self.update_continuum()

    def remove_node(self, node):
        if node in self.nodes:
            self.nodes.remove(node)
            self.update_continuum()
        else:
            raise ValueError("No such node %s to remove" % (node))

    # TODO implement secondary nodes??
    def get_node(self, key):
    
        size = len(self.continuum)
        if size == 0:
            node = None
        else:
            hash = self.hash_function(key)
            index = self.continuum.bisect_left(hash)
            if index < size:
                node = self.continuum.values()[index]
            else:
                node = self.continuum.values()[0]
                
        return node

    def update_continuum(self):
        
        tmp_dict = SortedDict()
        for node in self.nodes:
            for i in range(0, int(self.reps / 4)):
                for h in range(0, 4):
                    k = self.hash_function(self.get_key(node, i), h)
                    tmp_dict[k] = node
        
        self.continuum = tmp_dict;
  
    def get_key(self, node, rep_nr):
    
        key = node
        if key.startswith('/'):
            key = key[1:]
        return key + "-" + str(rep_nr);
        
    def get_nodes(self):
        return self.continuum
        
