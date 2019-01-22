#!/usr/bin/env python3

from jumpscale import j
import pandas as pd
import click


# example
# s = farmers()
# s.list()
# s.check_farm_existing('bishoy_farm')
# s.check_farm_nodes('bishoy_farm')

def check_farm_existing(myfarm):
    try:
        capacity = j.clients.threefold_directory.get(interactive=False)
        capacity.api.GetFarmer(myfarm)
        print('the farm {} is exist ....'.format(myfarm))
    except:
        print('the farm {} does not exist on our grid, check may no node are added to it '.format(self.myfarm))

click.command()
click.option('--farm', '-f', help='put your farm name ',required = True)
# get nodes using convert dict to list then use pandas class
def check_farm_nodes (myfarm):
    nodes =[]
    nodes_os = []
    last_updated = []
    capacity = j.clients.threefold_directory.get(interactive=False)
    resp = capacity.api.ListCapacity(query_params={'farmer': myfarm})[1]
    nodes = self.resp.json()
    for node in nodes:
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

if __name__ == '__main__':
    check_farm_nodes()