#!/usr/bin/env python3
from jumpscale import j
import os
import click
import time
import requests
import argparse
import sys

os.environ["LC_ALL"] = "en_US.UTF-8"
@click.group()
def cli():
    pass


@click.command()
def example():
    print ('you should use jumpscale9 and you should part of threefold.sysadmin itsyouonline organization ')
    print('usage example')
    print('./container.py create -n 10.102.53.47 --clientid 9Xk-W --clientsecret GjrFZ  -f https://hub.grid.tf/tf-bootable/ubuntu:18.04.flist -name ubuntu -p 2255:22 --sshkey "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8o0jEGYqe2k7J0TNL6Gg8h86ic3ReiC6THlBnOKPDiKProj/4uMTmi1Qf5OcLIdeHgcP+zy+ZL4kpP7N6VTALRPiTn6Lty6ZP+5mQocaJYosoGLzB6+lx1NW/zXtscv4V3goULiDEx9SBzSuD8wS0k00iHcRjmuFUIfERyYR8mjmWC/sRf1Y7qk9kQjFOLW5Sw0+RLrxr4l2ur/n8bDVgGVpzWypKIsqRU6Rf1HdXWmdAMCucPAkxR5WNies5QFOkyllxI6Fq+G9M0Uf+EubpfpC1oOMWjNFy781M4KZF+FXODcBlwevfvk0HH/5mTHOymIfwVV8vjRzycxjuQib3 pishoy@Bishoy-laptop"')
    print('to make data is persistent, saved your data in node itself do below:')
    print('    1 - list storagepool of node --> ./container.py liststoragepools -n 10.102.53.47 --clientid 9Xfsdfs --clientsecret Gjfsdfs')
    print('    2 - use one of storagepool that are shown form above command output as below')
    print('            ./container.py create -n 10.102.53.47 --clientid 9Xk-W --clientsecret GjrFZz  -f https://hub.grid.tf/tf-bootable/ubuntu:18.04.flist  -name ubunut_container -p 2299:22 --sshkey "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8o0jEGYqe2k7J0TNL6Gg8h86ic3ReiC6THlBnOKPDiKProj/4uMTmi1Qf5OcLIdeHgcP+zy+ZL4kpP7N6VTALRPiTn6Lty6ZP+5mQocaJYosoGLzB6+lx1NW/zXtscv4V3goULiDEx9SBzSuD8wS0k00iHcRjmuFUIfERyYR8mjmWC/sRf1Y7qk9kQjFOLW5Sw0+RLrxr4l2ur/n8bDVgGVpzWypKIsqRU6Rf1HdXWmdAMCucPAkxR5WNies5QFOkyllxI6Fq+G9M0Uf+EubpfpC1oOMWjNFy781M4KZF+FXODcBlwevfvk0HH/5mTHOymIfwVV8vjRzycxjuQib3 pishoy@Bishoy-laptop" -sp 18ded7c2-1069-474f-ab3e-851921c72b00 -v /nodesandbox:/containersandbox')
    print('    3 - note your data gonna be persistent in node in this dir /mnt/storagepools/ubunut_container/nodesandbox ')
    print ('also u can uninstall a service/container which will just stop container ')
    print ('     ./container.py uninstall -n 10.102.53.47 -iyocl 9Xk-W --clientsecret GjrFZzD -name test66')
    print('to delete a service use below will uninstall and delete the service/container')
    print('      ./container.py delete -n 10.102.53.47 -iyocl 9Xk-W --clientsecret GjrFZz -name test60')
def nodeconnect(node, clientid, clientsecret):
    data = {'host': node}
    params = {
        'grant_type': 'client_credentials',
        'client_id': clientid,
        'client_secret': clientsecret,
        'response_type': 'id_token',
        'scope': 'user:memberof:threefold.sysadmin'
    }
    url = 'https://itsyou.online/v1/oauth/access_token'
    resp = requests.post(url, params=params)
    resp.raise_for_status()
    jwt = resp.content.decode('utf8')
    if jwt:
        data['password_'] = jwt
    node_client = j.clients.zos.get('node', data=data)
    return node_client

def node_robot(node_client):
    nodeip = node_client.public_addr
    url = 'http://{}:6600'.format(nodeip)
    zrobot_cont = node_client.containers.get('zrobot')
    zrobottoken = zrobot_cont.client.bash('zrobot godtoken get').get()
    string = zrobottoken.stdout.split(":")[1]
    token = string.strip()
    j.clients.zrobot.new(node_client.name, data={'url': url, 'god_token_': token})
    node_robot = j.clients.zrobot.robots.get(node_client.name)
    return node_robot

@click.command()
@click.option('--node', '-n', required=True, help="remote node (ip)")
@click.option('--clientid', '-iyocl', required=True, help="itsyouonline client id")
@click.option('--clientsecret', '-iyoscret', required=True, help="itsyoonline client sceret")
def liststoragepools(node, clientid, clientsecret):
    node_client = nodeconnect(node, clientid, clientsecret)
    mylist = node_client.storagepools.list()
    for x in range(len(mylist)):
        print (mylist[x])
@click.command()
@click.option('--node', '-n', required=True, help="remote node (ip)")
@click.option('--name', '-name', required=True, help="container name of new FFP contianer")
@click.option('--ztid', '-ztid', required=False, help="zerotier network to join it ")
@click.option('--zttoken', '-zttoken', required=False, help="zerotier token to join it ")
@click.option('--storagepool', '-sp', required=False, help="storage pool data or be preistant")
@click.option('--ports', '-p', required=False, multiple=True, help="ports like '8080:80'")
@click.option('--flist', '-f', required=True, help="flist of container")
@click.option('--clientid', '-iyocl', required=True, help="itsyouonline client id")
@click.option('--clientsecret', '-iyoscret', required=True, help="itsyoonline client sceret")
@click.option('--mymounts', '-v', required=False, multiple=True,
              help="directory to be mounted like '/sandbox:/sandbox'")
@click.option('--sshkey', '-sshk', required=False, help="public ssh key to put insert in authorized keys")
def create(node, name, ztid, zttoken, storagepool, ports, flist, clientid, clientsecret, mymounts, sshkey):
    myflist = flist
    cont_name = name
    sp = storagepool
    ncl = nodeconnect(node, clientid, clientsecret)
    container_data = {
        'flist': myflist,
        'hostname': cont_name,
        'nics': [{'type': 'default'}]}
    if ztid:
        container_data['nics'] = [{'type': 'default'},
                                  {'type': 'zerotier', 'name': 'zerotier', 'id': ztid, 'ztClient': 'ztclientB'}]

    portlist = []
    if ports:
        for p in ports:
            portlist.append(p)
        container_data['ports'] = portlist

    mountsdict = {}
    mounts = []
    if storagepool and mymounts:
        for line in mymounts:
            mountlist = line.split(':')
            mountsdict[mountlist[0]] = mountlist[1]
        for k, v in mountsdict.items():
            create_mount = "mkdir -p /mnt/storagepools/%s/%s/%s" % (sp, cont_name, k)
            mount_path = "/mnt/storagepools/%s/%s/%s" % (sp, cont_name, k)
            ncl.client.bash(create_mount).get()
            mounts.append({'source': mount_path, 'target': v})
        container_data['mounts'] = mounts
    elif not storagepool and mymounts:
        print('Please provide us with storage pool name as two variables mymounts and storagepool should be exist togther')
        sys.exit()
    elif storagepool and not mymounts:
        print('Please provide mouting points as two variables mymounts and storagepool should be exist togther ')
        sys.exit()
    nrobot = node_robot(ncl)
    myargs = {'token': zttoken, }
    nrobot.services.find_or_create('github.com/threefoldtech/0-templates/zerotier_client/0.0.1', 'ztclientB',
                                       myargs)
    container = nrobot.services.create('github.com/threefoldtech/0-templates/container/0.0.1', cont_name,
                                           data=container_data)
    print('creating container .........')
    container.schedule_action('install').wait(die=True)

    if storagepool and mymounts:
        print('waiting 12 seconds till container get started then we can open ssh service  .........')
        time.sleep(12)
    else:
        print('waiting 5 seconds till container get started then we can open ssh service  .........')
        time.sleep(5)

    # import ipdb; ipdb.set_trace()
    if sshkey:
        mycontainer = ncl.containers.get(cont_name)
        mycontainer.client.bash('chmod 400 -R /etc/ssh/')
        mycontainer.client.bash('mkdir /root/.ssh')
        ssh_echo = 'echo "{}" >> /root/.ssh/authorized_keys'.format(sshkey)
        mycontainer.client.bash(ssh_echo)
        mycontainer.client.bash('/etc/init.d/ssh start')

@click.command()
@click.option('--node', '-n', required=True, help="remote node (ip)")
@click.option('--name', '-name', required=True, help="container name of new FFP contianer")
@click.option('--clientid', '-iyocl', required=True, help="itsyouonline client id")
@click.option('--clientsecret', '-iyoscret', required=True, help="itsyoonline client sceret")
def uninstall(node,name,clientid,clientsecret):
    node_client = nodeconnect(node,clientid,clientsecret)
    nrobot = node_robot(node_client)
    service = nrobot.services.get(name=name)
    service.schedule_action('uninstall').wait(die=True)

@click.command()
@click.option('--node', '-n', required=True, help="remote node (ip)")
@click.option('--name', '-name', required=True, help="container name of new FFP contianer")
@click.option('--clientid', '-iyocl', required=True, help="itsyouonline client id")
@click.option('--clientsecret', '-iyoscret', required=True, help="itsyoonline client sceret")
def delete(node,name,clientid,clientsecret):
    node_client = nodeconnect(node,clientid,clientsecret)
    nrobot = node_robot(node_client)
    service = nrobot.services.get(name=name)
    try:
        service.schedule_action('uninstall').wait(die=True)
    except:
        print ('there is expection in uninstalling service, gonna delete it ...')
    service.delete()
@click.command()
@click.option('--node', '-n', required=True, help="remote node (ip)")
@click.option('--clientid', '-iyocl', required=True, help="itsyouonline client id")
@click.option('--clientsecret', '-iyoscret', required=True, help="itsyoonline client")
def listcontainers(node,clientid,clientsecret):
    print ('this will list the container names not wihtout ids so it will takes a time, Please be patient')
    node_client = nodeconnect(node, clientid, clientsecret)
    contlist = node_client.containers.list()
    for x in range(len(contlist)):
        print (contlist[x])

if __name__ == "__main__":
    cli.add_command(liststoragepools)
    cli.add_command(create)
    cli.add_command(uninstall)
    cli.add_command(delete)
    cli.add_command(example)
    cli.add_command(listcontainers)
    cli()