from etc.fabric_tasks import *

env.username = os.environ.get('SSH_USERNAME', 'root')


def install_appserver():
    run("mkdir -p /srv/certs /srv/config /srv/apps /srv/htdocs /srv/build")
    run("chown -R %s:%s /srv/" % (env.username, env.username))


def reset_local_postgres():
    local('docker stop tpam_postgres_1')
    local('docker rm tpam_postgres_1')
    local('docker rm -v tpam_db_data_1')
    local('docker-compose up -d postgres')
