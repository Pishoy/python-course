from Jumpscale import j

log = j.logger.get('InstallingFreeFolwPages')
# j.logger.loggers_level_set(level='DEBUG')
# need to set mysql pass in flist # mysql -e 'SET PASSWORD FOR 'humhub'@'localhost' = PASSWORD("test");'
# add auto ssh keys in container then uplaod it to ssh productions server # ssh-keygen -b 2048 -t rsa -f ~/.ssh/rsa -q -N ""
# usage example
# python3 freefolw_install.py -n 10.102.114.69 -j "eyJhbGciOiJFUzM4vL4vi-Sn" --ztid "83048a0632bd58b2" --zttoken "fcUBv" --storagepool "2915c3ee-aa68-48ff-9737-57fe363951f0"

import click


def create_backup(production_ip, db_user, db_password,test_node_key):
    log.info('creating a backup (applicationa and database ) from production server .....')
    sshkey = j.clients.sshkey.get(instance='humhub_prod_key', data=dict(path='/root/.ssh/id_rsa'))
    sshclient = j.clients.ssh.get(instance="masterhh",
                                  data=dict(addr=production_ip, login="root", sshkey='humhub_prod_key',
                                            forward_agent=False, allow_agent=True, stdout=True, timeout=10),
                                  use_paramiko=True)
    backup_script = """
    echo {2} >> /root/.ssh/authorized_keys
    mkdir ~/humhub_backup
    mkdir -p ~/humhub_backup/protected
    
    mysqldump humhub -u {0} -p{1}> ~/humhub_backup/humhub.sql
    cp -r /var/www/html/humhub/themes ~/humhub_backup/themes
    cp -r /var/www/html/humhub/uploads ~/humhub_backup/uploads
    cp -r /var/www/html/humhub/protected/modules ~/humhub_backup/protected/
    cp -r /var/www/html/humhub/protected/config ~/humhub_backup/protected/
    cd ~/
    tar -czvf humhub_backup.tgz humhub_backup/*
    """.format(db_user, db_password,test_node_key)

    sshclient.execute(backup_script)


def restore(container_client,production_ip,db_user, db_password, test_db_humhub_user_passwd):
    log.info('restoring application and database from the ')
    restore_script = """
    cd /root
    scp root@{0}:/root/humhub_backup.tgz  .
    tar -zvxf humhub_backup.tgz
    mysql -u {1} -p{2} -D humhub  < humhub_backup/humhub.sql
    cp -r humhub_backup/* /var/www/html/humhub
    
    # change mysql password in humhub config to test environment password
    
    sed -i "s/.*'password' =>.*/      'password' => '{3}',/" /var/www/html/humhub/protected/config/dynamic.php
    
    mysql -u {1} -p{2} -e 'SET PASSWORD FOR 'humhub'@'localhost' = PASSWORD("{3}")'
    
    /usr/bin/php /var/www/html/humhub/protected/yii  queue/run
    /usr/bin/php /var/www/html/humhub/protected/yii  cron/run
    /usr/bin/php /var/www/html/humhub/protected/yii  search/rebuild 

    echo "DONE"
    """.format(production_ip, db_user, db_password, test_db_humhub_user_passwd)


    container_client.bash(restore_script).get()


def create_test_container(node, jwt, ztid, zttoken, storagepool):
    sp = storagepool
    mydir = 'freeflowBackup'
    data = {'host': node}
    if jwt:
        data['password_'] = jwt
    node_client = j.clients.zos.get(instance=node, data=data)
    nodeip = node_client.public_addr
    url = 'http://{}:6600'.format(nodeip)
    check = node_client.capacity.node_parameters()
    if check[0] not in 'support':
        log.error('Please note node does not in support mode, check if it is developement ... so you can comelete')
    zrobot_cont = node_client.containers.get('zrobot')
    zrobottoken = zrobot_cont.client.bash('zrobot godtoken get').get()
    string = zrobottoken.stdout.split(":")[1]
    token = string.strip()
    j.clients.zrobot.new(node_client.name, data={'url': url, 'god_token_': token})
    node_robot = j.clients.zrobot.robots.get(node_client.name)
    args = {'token': zttoken, }
    node_robot.services.find_or_create('github.com/threefoldtech/0-templates/zerotier_client/0.0.1', 'ztclientB',
                                       args)
    # create directory
    create_dir = "mkdir /mnt/storagepools/%s/%s" % (sp, mydir)
    backup_path = "/mnt/storagepools/%s/%s" % (sp, mydir)
    node_client.client.bash(create_dir).get()
    container_data = {
        'flist': 'https://hub.grid.tf/nashaatp/humhub.flist',
        'mounts': [{'source': backup_path, 'target': '/humhubBackup'}],
        'nics': [{'type': 'default'},
                 {'type': 'zerotier', 'name': 'zerotier', 'id': ztid, 'ztClient': 'ztclientB'}], }
    humhub_name = 'humhubtest'
    container = node_robot.services.find_or_create('github.com/threefoldtech/0-templates/container/0.0.1', humhub_name,
                                                   data=container_data)
    log.info('creating humhub container .........')
    container.schedule_action('install').wait(die=True)
    freeflowpages_test = node_client.containers.get(humhub_name)
    freeflowpages_test.client.bash('mkdir /root/.ssh').get()
    freeflowpages_test.client.bash('sleep 5;/etc/init.d/ssh start').get()
    freeflowpages_test.client.bash("ssh-keygen -t rsa -f /root/.ssh/id_rsa -q -P ''").get()
    key = freeflowpages_test.client.bash("cat /root/.ssh/id_rsa.pub").get()
    test_node_key = key.stdout
    freeflowpages_test.client.bash(
        'echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8o0jEGYqe2k7J0TNL6Gg8h86ic3ReiC6THlBnOKPDiKProj/4uMTmi1Qf5OcLIdeHgcP+zy+ZL4kpP7N6VTALRPiTn6Lty6ZP+5mQocaJYosoGLzB6+lx1NW/zXtscv4V3goULiDEx9SBzSuD8wS0k00iHcRjmuFUIfERyYR8mjmWC/sRf1Y7qk9kQjFOLW5Sw0+RLrxr4l2ur/n8bDVgGVpzWypKIsqRU6Rf1HdXWmdAMCucPAkxR5WNies5QFOkyllxI6Fq+G9M0Uf+EubpfpC1oOMWjNFy781M4KZF+FXODcBlwevfvk0HH/5mTHOymIfwVV8vjRzycxjuQib3 pishoy@Bishoy-laptop" >> /root/.ssh/authorized_keys').get()
    contIP = freeflowpages_test.client.zerotier.list()[0]['assignedAddresses'][1]
    container_IP = contIP.split("/")[0]
    print ('now you can access humhub continer by zerotier IP  ssh root@{}'.format(container_IP))
    return freeflowpages_test.client , test_cont_key


@click.command()
@click.option('--node', '-n', required=True, help="remote node (ip)")
@click.option('--jwt', '-j', help="optional node jwt")
@click.option('--ztid', '-ztid', required=True, help="zerotier network to join it ")
@click.option('--zttoken', '-zttoken', required=True, help="zerotier token to join it ")
@click.option('--storagepool', '-sp', required=True, help="storage pool that need to be create database/app backup")
@click.option('--production_ip', '-ip', required=True, help="production ip")
@click.option('--production_db_user', '-pu', required=True, help="production db_user")
@click.option('--production_db_passwd', '-ps', required=True, help="production db pass")
@click.option('--test_db_user', '-tu', required=True, help="test db_user")
@click.option('--test_db_passwd', '-ts', required=True, help="test db pass")
@click.option('--test_db_humhub_user_passwd', '-ths', required=True, help="test db humhub user pass")
def main(node, jwt, ztid, zttoken, storagepool, production_ip, production_db_user, production_db_passwd, test_db_user, test_db_passwd, test_db_humhub_user_passwd):
    import ipdb; ipdb.set_trace()
    test_client,test_node_key = create_test_container(node, jwt, ztid, zttoken, storagepool)

    # Backup
    create_backup(production_ip, production_db_user, production_db_passwd,test_node_key)

    # Restore
    restore(test_client,production_ip,test_db_user, test_db_passwd, test_db_humhub_user_passwd)


if __name__ == "__main__":
    main()
