from __future__ import with_statement
from fabric.api import env, local, run, task, settings, abort, put, cd, prefix, get, sudo
from fabric.contrib.project import rsync_project
import dotenv
import os

# Load local .env file

env.local_dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
dotenv.load_dotenv(env.local_dotenv_path)

# Set Fabric env
env.use_ssh_config = True
env.hosts = [os.environ.get('HOST_NAME', ''), ]

env.project_name = os.environ.get('PROJECT_NAME', '')
env.project_dir = os.path.join('/srv/apps/', env.project_name)
env.virtual_host = os.environ.get('VIRTUAL_HOST', '')
env.image_name = os.environ.get('IMAGE_NAME', '')
env.build_dir = '/srv/build'

env.dotenv_path = os.path.join(env.project_dir, '.env')

env.virtual_env = os.environ.get('VIRTUAL_ENV', '')
activate = {
    'osx': 'source activate %s' % env.virtual_env,
    'windows': 'activate %s' % env.virtual_env,
}
env.activate = activate['osx']

env.postgres_data = '/var/lib/postgresql/data'


def install_help():
    print('To install Pythor 3 Fabric, run:')
    print('pip install https://github.com/akaariai/fabric/archive/py34.zip')


def lol(cmd: str = '--help', path: str = '', live: bool = False):
    if not path:
        path = env.project_dir if live else './'

    with cd(path):
        run(cmd) if live else local(cmd)


def compose(cmd: str = '--help', path: str = '', live: bool = False) -> None:
    env_vars = 'IMAGE_NAME={image_name}'.format(image_name=env.image_name)
    template = "{env_vars} bash -c 'docker-compose {cmd}'".format(env_vars=env_vars, cmd=cmd)
    lol(cmd=template, path=path, live=live)


def docker_base(cmd: str = '--help', live: bool = False) -> None:
    template = 'docker {cmd}'.format(cmd=cmd)
    run(template) if live else local(template)


def docker(cmd: str = '--help', live: bool = False) -> None:
    docker_base(cmd=cmd, live=live)


def manage(cmd: str = 'help', live: bool = False) -> None:
    if live:
        compose('run --rm webapp ./manage.py {cmd}'.format(cmd=cmd), live=True)
    else:
        local('./src/manage.py {cmd}'.format(cmd=cmd))


def filr(cmd: str = 'get', file: str = '.envs') -> None:
    if cmd == 'get':
        get(os.path.join(env.project_dir, file), file)
    elif cmd == 'put':
        put(file, os.path.join(env.project_dir, file))
        run('chmod go+r {0}'.format(os.path.join(env.project_dir, file)))


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


def sqlite_reset():
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


def test_rsync():
    local(
            'rsync --delete --exclude ".git" --exclude ".gitignore" --exclude "__pycache__" --exclude "*.pyc" --exclude ".DS_Store" --exclude "environment.yml" --exclude "fabfile.py" --exclude "Makef ile" --exclude ".idea" --exclude "bower_components" --exclude "node_modules" --exclude "static" --exclude "var" --exclude "server.env" --exclude ".env.example" --exclude "requirements.txt"  --exclude "README.md" -pthrvz /data tpam:/srv/apps/tpam')


upload_command = """
rsync --delete --exclude ".git" --exclude ".gitignore" --exclude "__pycache__" --exclude "*.pyc" --exclude ".DS_Store" --exclude "environment.yml" --exclude "fabfile.py" --exclude "Makef ile" --exclude ".idea" --exclude "bower_components" --exclude "node_modules" --exclude "static" --exclude "var" --exclude "server.env" --exclude ".env.example" --exclude "requirements.txt"  --exclude "README.md" -pthrvz /data tpam:/srv/apps/tpam
"""


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


def postgres(cmd: str = 'backup', live: bool = False, tag: str = 'tmp'):
    """
    Task for backup and restore of database
    :param cmd:
    :param live:
    :param tag:
    :return:
    """

    backup_path = '/backup/db_backup.{tag}.tar.gz'.format(tag=tag)

    actions = {
        'backup':
            'tar -zcpf {backup_path} {data_path}'.format(
                    backup_path=backup_path,
                    data_path=env.postgres_data),
        'restore':
            'bash -c "tar xpf {backup_path} && chmod -R 700 {data_path}"'.format(
                    backup_path=backup_path,
                    data_path=env.postgres_data),
    }

    params = {
        'volumes_from': '--volumes-from {project_name}_db_data_1'.format(project_name=env.project_name),
        'volumes': '--volume ${PWD}/var/backups:/backup',
        'image': 'postgres',
        'cmd': actions[cmd],
    }

    docker_run_once = 'docker run --rm {volumes_from} {volumes} {image} {cmd}'
    compose('stop postgres', live=live)
    lol(docker_run_once.format(**params), live=live)
    compose('start postgres', live=live)


def postgres_everywhere():
    # local('echo ${DOCKER_HOST}')
    local('sudo sed -i "" "/[[:space:]]postgres$/d" /etc/hosts')
    local('sudo /bin/bash -c "echo $(echo ${DOCKER_HOST} | grep -oE \'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\')    postgres >> /etc/hosts"')


def datr(module: str = 'auth', target: str = 'local') -> None:
    """ Manage data
    :param module:
    :param target:

    Manually run this command:
        fab manage:'dumpdata -v 0 --indent 2 demo_app > ./src/data_dump.json',live=1
        fab filr:get,src/data_dump.json
        fab postgr
        fab manage:'loaddata ./src/dump_data.json'
    """

    if target == 'remote':
        manage('dumpdata -v 0 --indent 2 --natural-foreign {module} > ./src/data_dump.json'.format(
                module=module), live=False)
        filr('put', 'src/data_dump.json')
        postgres('backup', live=True)
        manage('loaddata data_dump.json', live=True)

    elif target == 'local':
        manage('dumpdata -v 0 --indent 2 --natural-foreign {module} > ./src/data_dump.json'.format(
                module=module), live=True)
        filr('get', 'src/data_dump.json')
        postgres('backup', live=False)
        manage('loaddata ./src/data_dump.json', live=False)
    else:
        print('Invalid option. Target must be local or remote')


# DANGER!!!
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
