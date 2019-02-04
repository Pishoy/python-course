from Jumpscale import j
logger = j.logger.get('installingFreeFolwPages')
import click

@click.command()
@click.option('--node', '-n', required=True, help="remote node (ip)")
@click.option('--jwt', '-j', help="optional node jwt")
@click.option('--ztid', '-ztid', required=True, help="zerotier network to join it ")
@click.option('--zttoken', '-zttoken', required=True, help="zerotier token to join it ")


def main(node, jwt,ztid,zttoken):
    data = {'host': node}
    if jwt:
        data['password_'] = jwt
    node_client = j.clients.zos.get(instance=node, data=data)
    nodeip = node_client.public_addr
    url = 'http://{}:6600'.format(nodeip)
    check = node_client.capacity.node_parameters()
    if check[0] not in 'support':
        logger = j.logger.error('Please note node does not in support mode, check if it is developement ... so you can comelete')
    zrobot_cont = node_client.containers.get('zrobot')
    zrobottoken = zrobot_cont.client.bash('zrobot godtoken get').get()
    string = zrobottoken.stdout.split(":")[1]
    token = string.strip()
    j.clients.zrobot.new(node_client.name,data={'url':url,'god_token_':token})
    node_robot = j.clients.zrobot.robots.get(node_client.name)
    args = {'token': zttoken,}
    zt = node_robot.services.create('github.com/threefoldtech/0-templates/zerotier_client/0.0.1', 'ztclientB', args)
    container_data = {
    'flist': 'https://hub.grid.tf/nashaatp/humhub.flist',
    'nics': [{'type': 'default'},{'type':'zerotier','name':'zerotier', 'id':zttoken,'ztClient':'ztclientB' }],}
    humhub_name = 'freeflowpages_test'
    container = node_robot.services.create('github.com/threefoldtech/0-templates/container/0.0.1', humhub_name, data=container_data)
    container.schedule_action('install').wait(die=True)
    freeflowpages_test = node_client.containers.get(humhub_name)
    freeflowpages_test.client.bash('mkdir /root/.ssh').get()
    freeflowpages_test.client.bash('echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8o0jEGYqe2k7J0TNL6Gg8h86ic3ReiC6THlBnOKPDiKProj/4uMTmi1Qf5OcLIdeHgcP+zy+ZL4kpP7N6VTALRPiTn6Lty6ZP+5mQocaJYosoGLzB6+lx1NW/zXtscv4V3goULiDEx9SBzSuD8wS0k00iHcRjmuFUIfERyYR8mjmWC/sRf1Y7qk9kQjFOLW5Sw0+RLrxr4l2ur/n8bDVgGVpzWypKIsqRU6Rf1HdXWmdAMCucPAkxR5WNies5QFOkyllxI6Fq+G9M0Uf+EubpfpC1oOMWjNFy781M4KZF+FXODcBlwevfvk0HH/5mTHOymIfwVV8vjRzycxjuQib3 pishoy@Bishoy-laptop" >> /root/.ssh/authorized_keys').get()

if __name__ == "__main__":
    main()