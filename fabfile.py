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


# Tasks
def init_dev():
    local('touch .env')
    local('conda env update')
    local('mkdir -p var/www/static')
    local('mkdir -p var/www/media')


def prepare():
    with prefix("export $(cat ./.env | grep -v ^# | xargs)"):
        with prefix("source activate %s" % env.virtual_env):
            local("echo $PROJECT_NAME")
            local("python ./src/manage.py makemigrations")
            local("./src/manage.py migrate")
            local("./src/manage.py collectstatic --noinput -v1")


def upload_app():
    rsync_project(
            env.project_dir, './',
            exclude=(
                '.git', '__pycache__', '.idea',
                'bower_components', 'node_modules',
                'static', 'var'),
            delete=True)


def upload_www():
    rsync_project(
            '/srv/htdocs/%s/' % env.project_name, './var/www/',
            exclude=('node_modules',))


def upload_config():
    put('./etc/nginx-vhost.conf', '/srv/config/%s' % env.virtual_host)
    run("sed -i 's/{{project_name}}/%s/g' '/srv/config/%s'" % (env.project_name, env.virtual_host))
    # put('./etc/certs/%s.key' % env.virtual_host, '/srv/certs/')
    # put('./etc/certs/%s.crt' % env.virtual_host, '/srv/certs/')


def deploy():
    prepare()
    upload_app()
    upload_www()
    upload_config()


def update_env():
    put('./environment.yml', '%s' % env.project_dir)
    docker_build()


def docker_build():
    with cd(env.project_dir):
        run("docker-compose build")


def docker_run():
    with cd(env.project_dir):
        run("docker-compose up -d")


def docker_clean():
    with cd(env.project_dir):
        run("docker-compose stop")
        run("docker-compose rm")


def start_proxy():
    run("docker run -d -p 80:80 -p 443:443  --name nginx-proxy \
        -v /srv/htdocs:/var/www:ro \
        -v /srv/certs:/etc/nginx/certs:ro \
        -v /srv/config/:/etc/nginx/vhost.d:ro \
        -v /var/run/docker.sock:/tmp/docker.sock:ro \
        jwilder/nginx-proxy")

    # run("docker restart nginx-proxy")
