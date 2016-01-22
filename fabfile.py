from __future__ import with_statement
from fabric.api import env, local, run, task, settings, abort, put, cd, prefix
from fabric.contrib.project import rsync_project
import dotenv
import os

# Load local .env file
env.local_dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(env.local_dotenv_path)

# Set Fabric env
env.use_ssh_config = True
env.hosts = [os.environ.get('HOST_NAME', ''), ]
env.project_name = os.environ.get('PROJECT_NAME', '')
env.virtual_env = os.environ.get('VIRTUAL_ENV', '')
env.virtual_host = os.environ.get('VIRTUAL_HOST', '')
env.image_name = os.environ.get('IMAGE_NAME', '')
env.project_dir = os.path.join('/srv/apps/', env.project_name)
env.build_dir = '/srv/build'
env.activate = 'source activate %s' % env.virtual_env
env.dotenv_path = os.path.join(env.project_dir, '.env')


def install_help():
    print('To install Pythor 3 Fabric, run:')
    print('pip install https://github.com/akaariai/fabric/archive/py34.zip')


def compose(cmd: str = '--help', path: str = '') -> None:
    if not path:
        path = env.project_dir

    with cd(path):
        run("IMAGE_NAME={image_name} bash -c 'docker-compose {cmd}'".format(
                cmd=cmd, image_name=env.image_name))


def docker(cmd: str = '--help') -> None:
    run('docker {cmd}'.format(cmd=cmd))


def manage(cmd: str = 'help') -> None:
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
    rsync_project(
            env.project_dir, './',
            exclude=(
                '.git', '.gitignore', '__pycache__', '*.pyc', '.DS_Store', 'environment.yml',
                'fabfile.py', 'Makefile', '.idea',
                'bower_components', 'node_modules',
                'static', 'var',
                'server.env', '.env.example', 'requirements.txt', 'README.md',
            ), delete=True)


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
        run('docker build -t {image_name} .'.format(
            image_name=env.image_name,
        ))

    # run('docker tag default_webapp kmaginary/apps:%s' % env.project_name)


def push_image():
    docker('push %s' % env.image_name)


def update_runtime():
    # make_wheels()
    make_default_webapp()


# def start_webapp():
#     run('IMAGE_NAME=kamginary/apps:dstack bash -c echo ${IMAGE_NAME}')


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


def wheel_backup():
    run('mv /srv/build/wheelhouse/* /srv/build/wheelhouse_backup')
    run('mkdir -p /srv/build/wheelhouse')
    run('cp /srv/build/wheelhouse_backup/Cython-0.23.4-cp35-cp35m-linux_x86_64.whl /srv/build/wheelhouse/')
    run('cp /srv/build/wheelhouse_backup/numpy-1.10.4-cp35-cp35m-linux_x86_64.whl /srv/build/wheelhouse/')
    run('cp /srv/build/wheelhouse_backup/scipy-0.16.1-cp35-cp35m-linux_x86_64.whl /srv/build/wheelhouse/')


def wheel_restore():
    run('mv /srv/build/wheelhouse_backup/* /srv/build/wheelhouse')


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


def config(action=None, key=None, value=None):
    '''Manage project configuration via .env

    e.g: fab config:set,<key>,<value>
         fab config:get,<key>
         fab config:unset,<key>
         fab config:list
    '''

    run('touch %(dotenv_path)s' % env)
    command = dotenv.get_cli_string(env.dotenv_path, action, key, value)
    run(command)


def update_self():
    """
    Function to update dstack. Please make sure all changes are commited before running.
    Still requires cleanup and testing.
    :return:
    """
    local('git commit -a -m "Autocommit before dstack update"')

    fp = './dstack-master/'
    local('wget https://github.com/jr-minnaar/dstack/archive/master.tar.gz')
    local('tar -zxvf master.tar.gz '
          '--strip=1 {fp}etc {fp}bin '
          '{fp}.dockerignore {fp}.gitignore '
          '{fp}fabfile.py {fp}docker-compose.yml'.format(fp=fp))
    local('rm master.tar.gz')
