init_dev: env
	conda env update
	touch .env
	mkdir -p var/www/static
	mkdir -p var/www/media

db_backup:
	docker run --rm --volumes-from $(PROJECT_NAME)_db_data_1 -v $(pwd)/var/backups:/backup postgres tar cpf /backup/db_backup.tar /var/lib/postgresql/data

db_restore:
	docker-compose stop
	docker run --rm --volumes-from $(PROJECT_NAME)_db_data_1 -v $(pwd)/var/backups:/backup postgres \
		bash -c "tar xpf /backup/db_backup.tar && chmod -R 700 /var/lib/postgresql/data"
	docker-compose start

clean_unused_volumes:
	- docker rm -v  $(docker ps --no-trunc -aq status=exited)
	- docker rmi $(docker images -q -f "dangling=true")
	docker run -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/docker:/var/lib/docker --rm martin/docker-cleanup-volumes

createsuperuser:
	docker-compose run --rm webapp bash -c "source activate $(PROJECT_NAME) && ./src/manage.py createsuperuser"

web_cli:
	docker-compose run --rm webapp bash

translate:
	source activate $(PROJECT_NAME) && ./src/manage.py makemessages -l af
	source activate $(PROJECT_NAME) && ./src/manage.py compilemessages

install_docker_root:
	apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D
	echo "deb https://apt.dockerproject.org/repo ubuntu-trusty main" >> /etc/apt/sources.list.d/docker.list
	apt-get update
	apt-get install docker-engine
	curl -L https://github.com/docker/compose/releases/download/1.5.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
	chmod +x /usr/local/bin/docker-compose
	docker run hello-world
	usermod -aG docker root


get_certificate:
	sudo docker run -it --rm -p 443:443 -p 80:80 --name letsencrypt \
			-v "/etc/letsencrypt:/etc/letsencrypt" \
			-v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
			quay.io/letsencrypt/letsencrypt:latest auth
