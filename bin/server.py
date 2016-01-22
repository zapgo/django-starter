import digitalocean
from dotenv import load_dotenv
import os

# Load local .env file
# env_path = os.path.join(os.path.dirname(__file__), '../server.env')
# load_dotenv(env_path)
load_dotenv('~/dstack/server.env')
token = os.environ.get('DIGITAL_OCEAN_TOKEN')

host_name = os.environ.get('HOST_NAME')
user_name = os.environ.get('USER_NAME')
sshd_port = os.environ.get('SSHD_PORT')
key_file_private = os.environ.get('KEY_FILE_PRIVATE')
key_file_public = os.environ.get('KEY_FILE_PUBLIC')
docker_compose_version = os.environ.get('DOCKER_COMPOSE_VERSION')
pptp_secret = os.environ.get('PPTP_SECRET')


def main():
    # curl http://169.254.169.254/metadata/v1/user-data

    ssh_public_key = read_public_key(key_file_public)

    config = {
        'token': token,
        "name": host_name,
        "region": "ams3",
        "size": "2gb",
        "image": "docker",
        'ssh_keys': [676628, ],
        "user_data": cloud_init_template.format(**{
            'user_name': user_name,
            'sshd_port': sshd_port,
            'docker_compose_version': docker_compose_version,
            'ssh_public_key': ssh_public_key,
            'pptp_secret': pptp_secret,
        }),
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
    manager = digitalocean.Manager(token=token)
    droplet_instance = manager.get_droplet(droplet_id)
    ip_address = droplet_instance.ip_address
    return ip_address


# droplet_instance.destroy()


def get_ssh_config(droplet_id):
    ip_address = (get_ip(droplet_id))

    ssh_config = ssh_config_template.format(
            host_name=host_name,
            ip=ip_address,
            port=sshd_port,
            user=user_name,
            keyfile=key_file_private,
    )

    print(ssh_config)
    return ssh_config


ssh_config_template = """Host {host_name}
    HostName {ip}
    Port {port}
    User {user}
    IdentityFile {keyfile}

"""

cloud_init_template = """#cloud-config
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
  - path: /srv/chap-secrets
    content: |
      # client    server      secret      acceptable local IP addresses
      canary      *           {pptp_secret}    *

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
  - docker pull mobtitude/vpn-pptp
  - docker run -d --privileged -p 1723:1723 -v /srv/chap-secrets:/etc/ppp/chap-secrets mobtitude/vpn-pptp
  - cd /srv/ && docker-compose up -d
"""
