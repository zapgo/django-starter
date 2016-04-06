from fabric.api import env, local, run, cd
import dotenv
import os

# Load local .env file
env.local_dotenv_path = os.path.join(os.path.dirname(__file__), './server.env')
dotenv.load_dotenv(env.local_dotenv_path)

# Set Fabric env
env.use_ssh_config = True
env.hosts = [os.environ.get('HOST_NAME', ''), ]

env.digital_ocean_token = os.environ.get('DIGITAL_OCEAN_TOKEN', '')
env.host_name = os.environ.get('HOST_NAME', '')

env.image_name = os.environ.get('IMAGE_NAME', '')

env.user_name = os.environ.get('USER_NAME', 'root')
env.sshd_port = os.environ.get('SSHD_PORT', '22')
env.key_file_private = os.environ.get('KEY_FILE_PRIVATE', '')
env.key_file_public = os.environ.get('KEY_FILE_PUBLIC', '')
env.docker_compose_version = os.environ.get('DOCKER_COMPOSE_VERSION', '1.5.2')
env.pptp_secret = os.environ.get('PPTP_SECRET', 'replace_with_real_password')


# How to create default deployment
def create_server(provider='digitalocean'):
    if provider=='digitalocean':
        local('docker-machine create '
              '--driver digitalocean '
              '--digitalocean-region=nyc2 '
              '--digitalocean-access-token={digital_ocean_token} '
              '{host_name}'.format(digital_ocean_token=env.digital_ocean_token,
                                   host_name=env.host_name))

    # for gcloud, first install gcloud and do gcloud auth login
    elif provider=='gcloud':
        local('docker-machine create '
              '--driver google '
              '--google-project zapgo-1273 '
              '--google-zone europe-west1-c '
              '--google-machine-type n1-standard-1 '
              '{host_name}'.format(host_name=env.host_name))


def create_ssh_config():
    ip_address = local('docker-machine ip {host_name}'.format(host_name=env.host_name), capture=True)
    keyfile = '~/.docker/machine/machines/{host_name}/id_rsa'.format(host_name=env.host_name)

    ssh_config = env.ssh_config_template.format(
        host_name=env.host_name,
        ip=ip_address,
        port=env.sshd_port,
        user=env.user_name,
        keyfile=keyfile,
    )
    local('echo "\nHost {host_name}\n\tHostName {ip}\n\tPort {ssh_port}\n\tUser {user}\n\tIdentityFile {keyfile}"'
          '>> ~/.ssh/config'.format(host_name=env.host_name,
                                     ip=ip_address,
                                     ssh_port=env.sshd_port,
                                     user=env.user_name,
                                     keyfile=keyfile))
    print(ssh_config)

def main():
    # curl http://127.0.0.1/metadata/v1/user-data

    ssh_public_key = read_public_key(env.key_file_public)

    config = {
        'token': env.digital_ocean_token,
        "name": env.host_name,
        "region": "ams3",
        "size": "2gb",
        "image": "docker",
        'ssh_keys': [676628, ],
        "user_data": env.userdata,
    }

    droplet = create_droplet(config)

    print(get_ip(droplet.id))
    print(get_ssh_config(droplet.id))

    return config


def read_public_key(path):
    # ssh_public_key = ''
    with open(path) as f:
        ssh_public_key = f.read().strip('\n')
    return ssh_public_key


def create_droplet(config):
    droplet = digitalocean.Droplet(**config)
    droplet.create()
    return droplet


def get_ip(droplet_id):
    manager = digitalocean.Manager(token=env.digital_ocean_token)
    droplet_instance = manager.get_droplet(droplet_id)
    ip_address = droplet_instance.ip_address
    return ip_address


# droplet_instance.destroy()


def get_ssh_config(droplet_id):
    ip_address = (get_ip(droplet_id))

    ssh_config = env.ssh_config_template.format(
            host_name=env.host_name,
            ip=ip_address,
            port=env.sshd_port,
            user=env.user_name,
            keyfile=env.key_file_private,
    )

    print(ssh_config)
    return ssh_config


env.ssh_config_template = """Host {host_name}
    HostName {ip}
    Port {port}
    User {user}
    IdentityFile {keyfile}

"""

env.cloud_init_template = """#cloud-config
package_upgrade: true
packages:
  - tree
  - vim
  - htop
groups:
  - docker: [{user_name},]
users:
  - name: {user_name}
    sudo: ['ALL=(ALL) NOPASSWD:ALL']
    groups: [sudo, docker]
    shell: /bin/bash
    ssh-authorized-keys:
      - {ssh_public_key}
write_files:
  - path: /srv/docker-compose.yml
    content: |
      nginx-proxy:
        image: jwilder/nginx-proxy
        ports:
          - 80:80
          - 443:443
        volumes:
          - /srv/htdocs:/var/www:ro
          - /srv/certs:/etc/nginx/certs:ro
          - /srv/config/:/etc/nginx/vhost.d:ro
          - /var/run/docker.sock:/tmp/docker.sock:ro

runcmd:
  - touch /init.txt
  - curl -L https://github.com/docker/compose/releases/download/{docker_compose_version}/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
  - chmod +x /usr/local/bin/docker-compose
  - mkdir -p /srv/certs /srv/config /srv/apps /srv/htdocs
  - chown -R {user_name}:{user_name} /srv/
  - sed -i -e '/^Port/s/^.*$/Port {sshd_port}/' /etc/ssh/sshd_config
  - sed -i -e '/^PermitRootLogin/s/^.*$/PermitRootLogin no/' /etc/ssh/sshd_config
  - sed -i -e '$aAllowUsers {user_name}' /etc/ssh/sshd_config
  - restart ssh
  - usermode -aG docker {user_name}
  - docker pull ubuntu
  - docker pull nginx
  - docker pull postgres
  - docker pull redis
  - docker pull rabbitmq:3-management
  - cd /srv/ && docker-compose up -d
"""

env.user_data = env.cloud_init_template.format(**{
    'user_name': env.user_name,
    'sshd_port': env.sshd_port,
    'docker_compose_version': env.docker_compose_version,
    'ssh_public_key': env.key_file_public,
    'pptp_secret': env.pptp_secret,
})


def install_appserver():
    run("mkdir -p /srv/certs /srv/config /srv/apps/default /srv/htdocs /srv/build")

    with cd('/srv/apps/default'):
        fp = 'django-starter-master/'
        run('wget https://github.com/zapgo/django-starter/archive/master.tar.gz')
        run('tar -zxvf master.tar.gz --strip=1 {fp}etc {fp}src {fp}docker-compose.yml'.format(fp=fp))
        run('rm master.tar.gz')

    run('cp /srv/apps/default/etc/server/docker-services.yml /srv/services.yml')

    run('docker-compose -f /srv/services.yml up -d nginx-proxy letsencrypt-plugin')
    run('docker pull zapgo/wheel-factory')

    with cd('/srv/build/'):
        fp = 'docker-image-factory-master'
        run('wget https://github.com/zapgo/docker-image-factory/archive/master.tar.gz')
        run('tar -zxvf master.tar.gz '
              '--strip=1'.format(fp=fp))
        run('rm master.tar.gz')

    run("chown -R %s:%s /srv/" % (env.user_name, env.user_name))


def install_unison():
    pass
# wget http://unison-binaries.inria.fr/files/2011.01.28-Esup-unison-2.40.61-linux-x8 6_64-text-static.tar.gz
# tar zxvf 2011.01.28-Esup-unison-2.40.61-linux-x86_64-text-static.tar.gz
# mv unison-2.40.61-linux-x86_64-text-static unison
# sudo ln -s /home/user/bin/unison /usr/bin/unison
