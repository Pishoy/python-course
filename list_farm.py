from jumpscale import j
import pandas as pd

# example
# s = farmers()
# s.list()
# s.check_farm_existing('bishoy_farm')

class farmers:
    def __init__(self):
        self.capacity = j.clients.threefold_directory.get(interactive=False)
        mylist, response = self.capacity.api.ListFarmers()
        self.farm_names = []
        for obj in mylist:
            self.farm_names.append(obj.name)
        #return self.farm_names


    def check_farm_existing (self,myfarm):
            self.myfarm = myfarm
            try:
                self.capacity.api.GetFarmer(self.myfarm)
                print ('the farm {} is exist ....'.format(self.myfarm))
            except:
                print ('the farm {} does not exist on our grid, check may no node are added to it '.format(self.myfarm))

# get nodes using convert dict to list then use pandas class
    def check_farm_nodes (self,myfarm):
        self.myfarm = myfarm
        nodes =[]
        nodes_os = []
        last_updated = []
        self.resp = self.capacity.api.ListCapacity(query_params={'farmer': self.myfarm})[1]
        self.nodes = self.resp.json()
        for node in self.nodes:
            node_id = node['node_id']
            nodes.append(node_id)
            os_version = node['os_version']
            nodes_os.append(os_version)
            updated = node['updated']
            last_updated.append(updated)
        #import ipdb;ipdb.set_trace()
        import pandas as pd
        table = pd.DataFrame({'node_id': nodes,
                              'os_version':nodes_os,
                              'last_updated' : last_updated})
        print ('Total number of nodes in this farm is {}'.format(len(nodes)))
        print (table[1:])

