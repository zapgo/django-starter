from fabric.api import env, local, run, task, settings, abort, put, cd, prefix, get, sudo, shell_env, open_shell, prompt
from fabric.colors import red, green, yellow, white
from fabric.context_managers import hide
from fabric.contrib.project import rsync_project
import os
import sys
import shutil
import logging
import re
import dotenv
from typing import Callable, Tuple
import posixpath

# Load local .env file
env.local_dotenv_path = os.path.join(os.path.dirname(__file__), '../.env')
dotenv.load_dotenv(env.local_dotenv_path)

# Set Fabric env
env.use_ssh_config = True
env.hosts = [os.environ.get('HOST_NAME', ''), ]

env.project_name = os.environ.get('PROJECT_NAME', '')
env.project_dir = posixpath.join('/srv/apps/', env.project_name)
env.virtual_host = os.environ.get('VIRTUAL_HOST', '')
env.image_name = os.environ.get('IMAGE_NAME', '')
env.build_dir = '/srv/build'

env.dotenv_path = os.path.join(env.project_dir, '.env')

env.virtual_env = os.environ.get('VIRTUAL_ENV', '')

activate = {
    'posix': 'source activate %s' % env.virtual_env,
    'nt': 'activate %s' % env.virtual_env,
}
env.os = os.name
env.activate = activate[env.os]

env.postgres_data = '/var/lib/postgresql/data'

env.project_path = os.path.dirname(os.path.dirname(__file__))

env.log_level = logging.DEBUG


def install_help():
    print('To install Python 3 Fabric, run:')
    print('pip Fabric3')


def lol(cmd: str = '--help', path: str = '', live: bool = False):
    if not path:
        path = env.project_dir if live else './'

    with cd(path):
        run(cmd) if live else local(cmd)


def compose(cmd: str = '--help', path: str = '', live: bool = False) -> None:
    env_vars = 'IMAGE_NAME={image_name} '.format(image_name=env.image_name)
    template = {
        'posix': '%sdocker-compose {cmd}' % (env_vars if live else ''),
        'nt': '%sdocker-compose {cmd}' % (env_vars if live else 'set PWD=%cd%&& '),
    }

    try:
        lol(cmd=template[env.os].format(cmd=cmd), path=path, live=live)
    except SystemExit:
        if not live:
            check_default_machine()


def docker_base(cmd: str = '--help', live: bool = False) -> None:
    template = 'docker {cmd}'.format(cmd=cmd)
    run(template) if live else local(template)


def docker(cmd: str = '--help', live: bool = False) -> None:
    docker_base(cmd=cmd, live=live)


def manage(cmd: str = 'help', live: bool = False) -> None:
    if live:
        compose('run --rm webapp manage.py {cmd}'.format(cmd=cmd), live=True)
    else:
        with prefix(env.activate):
            local('python src/manage.py {cmd}'.format(cmd=cmd))


def pip(cmd: str = '--help') -> None:
    with prefix(env.activate):
        local('pip {cmd}'.format(cmd=cmd))


def conda(cmd: str = '--help') -> None:
    with prefix(env.activate):
        local('conda {cmd}'.format(cmd=cmd))


def filr(cmd: str = 'get', file: str = '.envs', use_sudo: bool = False) -> None:
    if cmd == 'get':
        get(posixpath.join(env.project_dir, file), file)
    elif cmd == 'put':
        put(file, posixpath.join(env.project_dir, file), use_sudo=use_sudo)
        run('chmod go+r {0}'.format(posixpath.join(env.project_dir, file)))


# Tasks
def init():
    local('conda env update -f etc/environment.yml')
    local('pip install -r requirements.txt')
    if os.name == 'nt':
        local('pip install etc\windows\psycopg2-2.6.1-cp35-none-win_amd64.whl')
    # TODO handle path creation natively
    try:
        local('mkdir %s' % os.path.abspath('./var/www/static'))
        local('mkdir %s' % os.path.abspath('./var/www/media'))
    except:
        pass


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
    compose(cmd='-f service.yml -p %s run --rm wheel-factory' % env.project_name, path='/srv/build', live=True)


def make_default_webapp():
    put('./requirements.txt', '/srv/build/requirements.txt')

    with cd('/srv/build'):
        run('docker build -t {image_name} .'.format(
            image_name=env.image_name,
        ))

        # run('docker tag default_webapp kmaginary/apps:%s' % env.project_name)


def push_image(live: bool = False):
    docker('push %s' % env.image_name, live=live)


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

    backup_name = 'db_backup.{tag}.tar.gz'.format(tag=tag)
    backup_path = posixpath.join('/backup/', backup_name)

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

    if live:
        backup_to_path = posixpath.join(env.project_dir, 'var/backups')
    else:
        backup_to_path = os.path.join(env.project_path, 'var/backups')

    params = {
        'volumes_from': '--volumes-from {0}_db_data_1'.format(env.project_name),
        'volumes': '--volume {0}:/backup'.format(backup_to_path),
        'image': 'postgres',
        'cmd': actions[cmd],
    }

    docker_run_once = 'docker run --rm {volumes_from} {volumes} {image} {cmd}'
    if live and cmd == 'restore':
        answer = prompt('Do you first want to upload the backup?', default='no', )
        if answer == 'yes':
            filr(cmd='put', file=os.path.join('var/backups/', backup_name), use_sudo=True)
    compose('stop postgres', live=live)
    lol(docker_run_once.format(**params), live=live)
    compose('start postgres', live=live)
    if live and cmd == 'backup':
        answer = prompt('Did you want to download backup?', default='no', )
        if answer == 'yes':
            filr(cmd='get', file=posixpath.join('var/backups/', backup_name))


def reset_local_postgres():
    import time
    timestamp = int(time.time())
    postgres('backup', tag=str(timestamp))
    docker('stop %s_postgres_1' % env.project_name)
    docker('rm -v %s_postgres_1' % env.project_name)
    docker('rm -v %s_db_data_1' % env.project_name)
    compose('up -d postgres')


def postgres_everywhere():
    # local('echo ${DOCKER_HOST}')
    local('sudo sed -i "" "/[[:space:]]postgres$/d" /etc/hosts')
    local('sudo /bin/bash -c "echo $(echo ${DOCKER_HOST} | '
          'grep -oE \'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\')    postgres >> /etc/hosts"')


def datr(module: str = 'auth', target: str = 'local') -> None:
    """ Manage data
    :param module:
    :param target:

    Manually run this command:
        fab manage:'dumpdata -v 0 --indent 2 assessment > ./src/data_dump.json',live=1
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
        answer = prompt('Do you want to install data locally?', default='no', )
        if answer == 'yes':
            postgres('backup', live=False)
            manage('loaddata ./src/data_dump.json', live=False)
    else:
        print('Invalid option. Target must be local or remote')


# DANGER!!!
def clean_unused_volumes():
    with settings(warn_only=True):
        run('docker rm -v  $(docker ps --no-trunc -aq status=exited)')
        run('docker rmi $(docker images -q -f "dangling=true")')

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


def doctor():
    checkup(check_virtual_env,
            description='Python virtualenv checkup...',
            success='Everything is looking good',
            error='Project environment does not exist. To fix, run\n > conda env create -f etc/environment.yml', )

    check_default_machine()
    check_env_vars()
    check_postgres()

    checkup(check_depencies,
            description='Checking dependencies...',
            success='All dependencies installed',
            error='Please install missing dependencies', )


def checkup(check_function: Callable[[None], dict], description: str = 'Checking...',
            success: str = 'No problem', error: str = 'Errors found'):
    if env.log_level <= logging.DEBUG:
        print(description)

    result = check_function()

    if result['success']:
        if env.log_level <= logging.INFO:
            print(green(success))
    else:
        if env.log_level <= logging.WARNING:
            print(red(error, bold=True))


def check_depencies():
    success = True

    dependencies = [
        'git', 'python', 'conda', 'pip', 'rsync', 'wget', 'curl', 'grep', 'ssh',
        'docker', 'docker-compose', 'docker-machine', 'fab', 'node', 'bower'
    ]

    if os.name == 'nt':
        dependencies += ['choco', ]
    elif sys.platform == 'darwin':
        dependencies += ['brew', ]

    unmet = 0

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

            if env.log_level <= logging.DEBUG:
                print('{0} {1:15} {2:20} {3}'.format(
                    green(' O', bold=True), dependency, yellow(version[0], bold=True), os.path.abspath(path)))
        else:
            if env.log_level <= logging.WARNING:
                print(red(' X', bold=True), ' ', dependency)

            unmet += 1

    if unmet > 0:
        success = False

    return {'success': success,}


def check_virtual_env():
    success = True

    conda_envs = get_result('conda info --envs')
    conda_envs = conda_envs.split('\n')[2:]

    for cenv in conda_envs:
        project_env_line = cenv.find(env.virtual_env) != -1

        if cenv.find('*') and project_env_line:
            if env.log_level <= logging.INFO:
                print(green('Project environment found and active:'))
                print(white(cenv))
        elif project_env_line:
            if env.log_level <= logging.WARNING:
                print(yellow('Project environment found, but not activated'))
                print(white('To fix, run:\n > activate tpam'))
            success = False

    return {'success': success, }


def check_default_machine():
    if env.log_level <= logging.INFO:
        print(white('\nDocker checkup', bold=True))

    env_cmd = {
        'nt': 'FOR /f "tokens=*" %i IN (\'docker-machine env default\') DO %i',
        'posix': 'eval $(docker-machine env default)'
    }

    line = red('#' * 74)

    # check3 = 0
    default_machine = get_result('docker-machine ls --filter name=default')
    machines = default_machine.split('\n')
    if len(machines) > 1:
        default_machine = machines[1]
        if default_machine.find('Running') != -1 and default_machine.find('*') != -1:
            if env.log_level <= logging.INFO:
                print(green('Default machine running and active'))
        elif default_machine.find('Running') != -1 and default_machine.find('-') != -1:
            if env.log_level <= logging.INFO:
                print(yellow('Warning: Default machine running but not active'))
                print(line)
                print(' > ' + env_cmd[env.os])
                print(line)
        else:
            if env.log_level <= logging.INFO:
                print(yellow('Warning: Default machine found but not running'))
                print(line)
                print(' > docker-machine start default')
                print(' > ' + env_cmd[env.os])
                print(line)

    else:
        if env.log_level <= logging.WARNING:
            print(red('Error: Default machine does not exist'))
            print(line)
            print(white('Create using:\n > docker-machine create --driver virtualbox default'))
            print(' > docker-machine start default')
            print(' > ' + env_cmd[env.os])
            print(line)


def check_env_vars():
    if env.log_level <= logging.INFO:
        print(white('\nEnvironment checkup', bold=True))

    envs = ['HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY', 'http_proxy', 'https_proxy', 'no_proxy', 'conda_default_env']
    for e in envs:
        value = os.environ.get(e, '')
        if value:
            if env.log_level <= logging.INFO:
                print('{0} {1:15} = {2:20}'.format(
                    yellow(' >', bold=True), e, yellow(value, bold=True)))
        else:
            if env.log_level <= logging.INFO:
                print('{0} {1:15}'.format(
                    yellow(' >', bold=True), e))

    if env.log_level <= logging.INFO:
        print(green('Everything is looking good!'))

    if env.log_level <= logging.INFO:
        print(white('\nChecking for .env file', bold=True))

    mandatory_envs = ['SITE_ID', 'DEBUG']
    if os.path.exists('./.env'):
        if env.log_level <= logging.INFO:
            print(green('Found .env file'))
        os.environ.get('PATH', '')
    else:
        if env.log_level <= logging.ERROR:
            print(red('.env does not exist!'))


def check_postgres():
    # docker-machine ssh {host_name} -C "echo `pbpaste` >> .ssh/authorized_keys"

    if env.log_level <= logging.INFO:
        print(white('\nChecking for postgres entry in hosts file', bold=True))
    try:
        import socket
        ip = socket.gethostbyname('postgres')
        if ip:
            if env.log_level <= logging.INFO:
                print(green("Postgres IP is %s" % ip))
    except:
        if env.log_level <= logging.ERROR:
            print(red("Hostname not set!"))


def get_result(cmd: str = 'echo "Hello, World!'):
    with hide('output', 'running', 'warnings'), settings(warn_only=True):
        result = local(cmd, capture=True)
        return result if result else ''
