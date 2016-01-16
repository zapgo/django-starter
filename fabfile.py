from __future__ import with_statement
from fabric.api import env, local, run, settings, abort, put, cd, prefix
from fabric.contrib.project import rsync_project
from dotenv import load_dotenv
import os

# Load local .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Set Fabric env
env.use_ssh_config = True
env.hosts = [os.environ.get('HOST_NAME', ''), ]
env.project_name = os.environ.get('PROJECT_NAME', '')
env.virtual_env = os.environ.get('VIRTUAL_ENV', '')
env.virtual_host = os.environ.get('VIRTUAL_HOST', '')
env.project_dir = os.path.join('/srv/apps/', env.project_name)
env.build_dir = '/srv/build'
env.activate = 'source activate %s' % env.virtual_env


def compose(cmd: str = '--help', path: str = ''):
    if not path:
        path = env.project_dir

    with cd(path):
        run('docker-compose {cmd}'.format(cmd=cmd))


def manage(cmd: str = 'help'):
    local('./src/manage.py {cmd}'.format(cmd=cmd))


# Tasks
def init_dev():
    local('touch .env')
    local('conda env update')
    local('mkdir -p var/www/static')
    local('mkdir -p var/www/media')


def prepare():
    with prefix(env.activate):
        manage('makemigrations')
        manage('migrate')
        manage('collectstatic --noinput -v1')


def translate():
    with prefix(env.activate):
        manage('makemessages -l af')
        manage('compilemessages')


def backup_basics():
    with prefix(env.activate):
        manage('dumpdata --indent=2 '
               'flatpages sites auth.users auth.groups > '
               'src/config/fixtures/initial_data.json')


def local_db_reset():
    with prefix("export $(cat ./.env | grep -v ^# | xargs)"):
        with prefix(env.activate):
            local("echo $PROJECT_NAME")
            local("mv ./src/db.sqlite3 ./src/db.sqlite3.bak")
            local('find . -path "*/migrations/*.py" -not -name "__init__.py" -delete')
            manage('makemigrations')
            manage('migrate')
            manage('collectstatic --noinput -v1')
            manage('loaddata ./src/config/fixtures/initial_data.json')
            # manage('loaddata ./src/customer_management/fixtures/initial_data.json')


def upload_app():
    rsync_project(env.project_dir, './',
                  exclude=('.git', '__pycache__', '.idea', 'bower_components', 'node_modules', 'static', 'var',),
                  delete=True)


def upload_www():
    rsync_project('/srv/htdocs/%s/' % env.project_name, './var/www/', exclude=('node_modules',))


def upload_config():
    put('./etc/nginx-vhost.conf', '/srv/config/%s' % env.virtual_host)
    run("sed -i 's/{{project_name}}/%s/g' '/srv/config/%s'" % (env.project_name, env.virtual_host))
    try:
        put('./etc/certs/%s.key' % env.virtual_host, '/srv/certs/')
        put('./etc/certs/%s.crt' % env.virtual_host, '/srv/certs/')
    except:
        print('No certs found')


def deploy():
    prepare()
    upload_app()
    upload_www()
    upload_config()

# wget https://github.com/jr-minnaar/wheel-factory/archive/master.tar.gz
# tar xzvf master.tar.gz -C build --strip-components=1
# rm master.tar.gz

# cp /srv/apps/gauseng/etc/build-requirements.txt /srv/build/requirements.txt
# cd /srv/build && docker-compose -f service.yml -p gauseng run --rm wheel-factory
# cd /srv/build && docker build -t gauseng_base .
# rm -rf /srv/build/wheelhouse/*
# cd /srv/apps/tpam && docker-compose build --no-cache && docker-compose up


def make_wheels():
    put('./etc/build-requirements.txt', '/srv/build/build-requirements.txt')
    compose('-f service.yml -p %s run --rm wheel-factory' % env.project_name, '/srv/build')


def make_default_webapp():
    put('./requirements.txt', '/srv/build/requirements.txt')

    with cd('/srv/build'):
        run('docker build -t default_webapp .')

    run('docker tag default_webapp kmaginary/apps:%s' % env.project_name)


def docker_build_app():
    compose('build', env.project_dir)


def update_runtime():
    # make_wheels()
    make_default_webapp()
    docker_build_app()


def start_proxy():
    run("docker run -d -p 80:80 -p 443:443  --name nginx-proxy \
        -v /srv/htdocs:/var/www:ro \
        -v /srv/certs:/etc/nginx/certs:ro \
        -v /srv/config/:/etc/nginx/vhost.d:ro \
        -v /var/run/docker.sock:/tmp/docker.sock:ro \
        jwilder/nginx-proxy")

    # run("docker restart nginx-proxy")


def db_backup():
    with cd(env.project_dir):
        run('docker run --rm '
            '--volumes-from {project_name}_db_data_1 '
            '-v ./var/backups:/backup postgres '
            'tar cpf /backup/db_backup.tar /var/lib/postgresql/data'.format(project_name=env.project_name))


def db_restore():
    compose('stop')

    with cd(env.project_dir):
        run('docker run --rm '
            '--volumes-from {project_name}_db_data_1 '
            '-v ./var/backups:/backup postgres '
            'bash -c "tar xpf /backup/db_backup.tar && chmod -R 700 /var/lib/postgresql/data"'.format(
                project_name=env.project_name))

    compose('start')


def clean_unused_volumes():
    try:
        run('docker rm -v  $(docker ps --no-trunc -aq status=exited)')
    except:
        pass
    try:
        run('docker rmi $(docker images -q -f "dangling=true")')
    except:
        pass

    run('docker run --rm'
        '-v /var/run/docker.sock:/var/run/docker.sock '
        '-v /var/lib/docker:/var/lib/docker '
        'martin/docker-cleanup-volumes')
