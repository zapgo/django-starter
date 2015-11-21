PROJECT_NAME = dstack

build_project:
	touch .env

db_backup:
	docker run --rm --volumes-from $(PROJECT_NAME)_db_data_1 -v $(pwd)/var/backups:/backup postgres tar cpf /backup/db_backup.tar /var/lib/postgresql/data


deploy:
	./src/manage.py collectstatic -v1 --no-input
	rsync -rPh --exclude '.git' --exclude '__pycache__' --exclude '.idea' ../$(PROJECT_NAME) europe:/app/

install:
	ssh europe -c "ln -s /app/$(PROJECT_NAME)/etc/nginx/tpam.ga.conf /app/$(PROJECT_NAME)/config/tpam.ga"
	ssh europe -c "ln -s /app/$(PROJECT_NAME)/etc/nginx/tpam.ga.conf /app/$(PROJECT_NAME)/config/www.tpam.ga"

db_restore:
	docker-compose stop
	docker run --rm --volumes-from $(PROJECT_NAME)_db_data_1 -v $(pwd)/var/backups:/backup postgres \
		bash -c "tar xpf /backup/db_backup.tar && chmod -R 700 /var/lib/postgresql/data"
	docker-compose start

start_proxy:
	docker run -d -p 80:80 -v /var/run/docker.sock:/tmp/docker.sock:ro jwilder/nginx-proxy

clean_unused_volumes:
	docker rm -v `docker ps --no-trunc -aq`
	docker run -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/docker:/var/lib/docker --rm martin/docker-cleanup-volumes
	docker rmi $(docker images -f "dangling=true" -q)

createsuperuser:
	docker-compose run --rm webapp bash -c "source activate dstack && ./src/manage.py createsuperuser"

web_cli:
	docker-compose run --rm webapp bash

translate:
	source activate dstack && ./src/manage.py makemessages -l af
	source activate dstack && ./src/manage.py compilemessages

install_docker_root:
	apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
	echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" >> /etc/apt/sources.list.d/docker.list
	apt-get update
	apt-get install docker-engine
	curl -L https://github.com/docker/compose/releases/download/1.5.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
	chmod +x /usr/local/bin/docker-compose
	docker run hello-world
	usermod -aG docker root

