from fabric.api import env, local, run, prompt, task, settings, abort, put, cd, prefix, get, sudo
from fabric.context_managers import hide
from fabric.contrib.project import rsync_project
import dotenv
import os
import sys
import shutil
import re
from fabric.api import env, local
from fabric.colors import red, green, yellow, white
from typing import Tuple


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
    print('pip install Fabric3')


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
    local(
        'sudo /bin/bash -c "echo $(echo ${DOCKER_HOST} | grep -oE \'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\')    postgres >> /etc/hosts"')


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


def release(live: bool = False, tag: str = 'tmp'):
    # if tag == 'tmp':
    #     release = prompt('Please supply a release name', validate=r'^\w+-\d+(\.\d+)?$')

    answer = prompt('Did you remember to first commit all changes??', default='no', )
    if answer == 'yes':
        try:
            local('git tag %s' % tag)
        except:
            pass
        postgres('backup', live=live, tag=tag)
        docker('tag {image_name}:latest {image_name}:{tag}'.format(
                image_name=env.image_name, tag=tag))
    else:
        print("# Commit changes using:\n$ git commit -a -m 'message...'")


def rollback(live: bool = False, tag: str = 'tmp'):
    answer = prompt('Did you remember to first release?', default='no', )
    # print(answer)
    if answer == 'yes':
        local('git branch development')
        local('git reset --hard %s' % tag)
        postgres('restore', live=live, tag=tag)
        docker('tag {image_name}:{tag} {image_name}:latest'.format(
                image_name=env.image_name, tag=tag))
    else:
        print("# You can do a release by running:\n$ fab release:tag='tag'")


def update_self(files: Tuple[str] = (1, 'src/config', 'fabfile.py', 'docker-compose.yml')):
    """
    Function to update dstack. Please make sure all changes are commited before running.
    Still requires cleanup and testing.
    :param files:
    :return:
    """
    extract_files = ' {fp}'.join(files)

    with settings(warn_only=True):
        local('git commit -a -m "Autocommit before dstack update"')

    local('wget https://github.com/jr-minnaar/dstack/archive/master.tar.gz')
    local('tar -zxvf master.tar.gz --strip=1' + extract_files.format(fp='dstack-master/'))
    local('rm master.tar.gz')



dependency_versions = {
    'git': '2.7.1',
    'python': '3.5.1',
    'conda': '3.14.1',
    'pip': '8.0.2',
    'rsync': '2.6.9',
    'wget': '1.17.1',
    'curl': '7.43.0',
    'grep': '2.5.1',
    'ssh': '1',
    'docker': '1.10.1',
    'docker-compose': '1.6.0',
    'docker-machine': '0.6.0',
    'fab': '1.10.2',
    'brew': '0.9.5',
}

import logging


def doctor(log_level: int = logging.INFO):
    log_level = int(log_level)
    dependencies = [
        'git', 'python', 'conda', 'pip', 'rsync', 'wget', 'curl', 'grep', 'ssh',
        'docker', 'docker-compose', 'docker-machine', 'fab', 'node', 'bower'
    ]

    if os.name == 'nt':
        dependencies += ['cinst', ]
    elif sys.platform == 'darwin':
        dependencies += ['brew', ]

    unmet = 0

    if log_level <= logging.DEBUG:
        print('Dependency checkup...')
    for dependency in dependencies:
        path = shutil.which(dependency)
        version = ['', ]
        if path:
            if dependency not in ['ssh', ]:
                version_raw = get_result(path + ' --version')
                try:
                    version = re.findall(r'\d+\.\d+\.\d?', version_raw.stderr if version_raw.stderr else version_raw)
                except:
                    pass
            if not version:
                version = ['', ]

            if log_level <= logging.DEBUG:
                print('{0} {1:15} {2:20} {3}'.format(
                    green(' O', bold=True), dependency, yellow(version[0], bold=True), os.path.abspath(path)))
        else:
            if log_level <= logging.WARNING:
                print(red(' X', bold=True), ' ', dependency)
                unmet += 1

    if unmet > 0:
        if log_level <= logging.WARNING:
            print(red('Please install missing dependencies', bold=True))
    else:
        if log_level <= logging.INFO:
            print(green('Everything is looking good!'))

    if log_level <= logging.INFO:
        print(white('\nEnvironment checkup', bold=True))

    envs = ['HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'no_proxy', 'conda_default_env']
    for e in envs:
        value = os.environ.get(e, '')
        if value:
            if log_level <= logging.INFO:
                print('{0} {1:15} = {2:20}'.format(
                    yellow(' >', bold=True), e, yellow(value, bold=True)))
        else:
            if log_level <= logging.INFO:
                print('{0} {1:15}'.format(
                    yellow(' >', bold=True), e))

    if log_level <= logging.INFO:
        print(green('Everything is looking good!'))

    if log_level <= logging.INFO:
        print(white('\nPython virtualenv checkup', bold=True))
    check3 = 0
    conda_envs = get_result('conda info --envs')

    conda_envs = conda_envs.split('\n')[2:]
    for cenv in conda_envs:
        if cenv.find('*') and cenv.find(env.virtual_env) != -1:
            if log_level <= logging.INFO:
                print(green('Project environment found and active:'))
                print(white(cenv))
            check3 = 1
        elif cenv.find(env.virtual_env) != -1:
            if log_level <= logging.WARNING:
                print(yellow('Project environment found, but not activated'))
                print(white('To fix, run:\n > activate %s' % env.virtual_env))
            check3 = 1
        else:
            pass
            #if log_level <= logging.ERROR:
            #    print(red('Project environment does not exist'))
            #    print(white('To fix, run:\n > conda env create -f etc/environment.yml'))
            #check3 += 1

    if check3 != 1:
        if log_level <= logging.INFO:
            print(red('Project environment does not exist'))

    if log_level <= logging.INFO:
        print(white('\nDocker checkup', bold=True))

    # check3 = 0
    # default_machine = get_result('docker-machine ls --filter name=default')
    # print(default_machine.split('\n')[1])
    # if default_machine.find('Running') != -1 and default_machine.find('*') != -1:
    #     print(green('Default machine running and active'))
    # elif default_machine.find('*') != -1:
    #     print(yellow('Default machine found but not running'))

    check_default_machine()

    if log_level <= logging.INFO:
        print(white('\nChecking for .env file', bold=True))

    mandatory_envs = ['SITE_ID', 'DEBUG']
    if os.path.exists('./.env'):
        if log_level <= logging.INFO:
            print(green('Found .env file'))
        os.environ.get('PATH')
    else:
        if log_level <= logging.ERROR:
            print(red('.env does not exist!'))
    if log_level <= logging.INFO:
        print(white('\nChecking for postgres entry in hosts file', bold=True))
    try:
        import socket
        ip = socket.gethostbyname('postgres')
        if ip:
            if log_level <= logging.INFO:
                print(green("Postgres IP is %s" % ip))
    except:
        if log_level <= logging.ERROR:
            print(red("Hostname not set!"))


def get_result(cmd: str = 'echo "Hello, World!'):
    with hide('output', 'running', 'warnings'), settings(warn_only=True):
        result = local(cmd, capture=True)
        return result if result else ''


def check_default_machine():
    status = get_result('docker-machine status default')
    # line = red('#' * 74)
    env_cmd = {
        'nt': 'FOR /f "tokens=*" %i IN (\'docker-machine env default\') DO %i',
        'posix': 'eval $(docker-machine env default)'
    }
    print(yellow('Needs configuring:'), green('# Run this command to configure your shell: '))
    # print(line)
    if status == 'Running':
        print(' > ' + env_cmd[os.name])
    else:
        print(' > docker-machine start default')
        print(' > ' + env_cmd[os.name])
    # print(line)
