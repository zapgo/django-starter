env:
	export $(cat ./.env | grep -v ^# | xargs)

#source activate ${PROJECT_NAME}
#clear_env
#env $(cat .env | xargs)

init_dev: env
	conda env update
	touch .env
	mkdir -p var/www/static
	mkdir -p var/www/media

prepare: env
	./src/manage.py makemigrations
	./src/manage.py migrate
	./src/manage.py collectstatic --noinput -v1

deploy: prepare
	rsync -rPh \
		--exclude '.git' \
		--exclude '__pycache__' \
		--exclude '.idea' \
		--exclude 'bower_components' \
		--exclude 'node_modules' \
		../$(PROJECT_NAME) $(HOST_NAME):/apps/

install:
	env $(cat .env | xargs) && ssh $(HOST_NAME) -c "ln -s \
		/apps/$(PROJECT_NAME)/etc/nginx/$(VIRTUAL_HOST).conf \
		/apps/$(PROJECT_NAME)/config/$(VIRTUAL_HOST)"

run:
	ssh $(HOST_NAME) "cd /apps/$(PROJECT_NAME)/ && docker-compose up -d"

clean_run:
	ssh $(HOST_NAME) "cd /apps/$(PROJECT_NAME)/ && docker-compose stop && docker-compose rm && docker-compose up -d"

db_backup:
	docker run --rm --volumes-from $(PROJECT_NAME)_db_data_1 -v $(pwd)/var/backups:/backup postgres tar cpf /backup/db_backup.tar /var/lib/postgresql/data

db_restore:
	docker-compose stop
	docker run --rm --volumes-from $(PROJECT_NAME)_db_data_1 -v $(pwd)/var/backups:/backup postgres \
		bash -c "tar xpf /backup/db_backup.tar && chmod -R 700 /var/lib/postgresql/data"
	docker-compose start

clean_unused_volumes:
	docker rm -v `docker ps --no-trunc -aq`
	docker run -v /var/run/docker.sock:/var/run/docker.sock -v /var/lib/docker:/var/lib/docker --rm martin/docker-cleanup-volumes
	docker rmi $(docker images -f "dangling=true" -q)

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

reload_server:
	ssh $(HOST_NAME) "cd /apps/$(PROJECT_NAME)/; docker-compose restart;"


get_certificate:
	sudo docker run -it --rm -p 443:443 -p 80:80 --name letsencrypt \
			-v "/etc/letsencrypt:/etc/letsencrypt" \
			-v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
			quay.io/letsencrypt/letsencrypt:latest auth

run_proxy:
	sudo docker run -d -p 80:80 -p 443:443  --name nginx-proxy \
		-v /apps/$(PROJECT_NAME)/var/www/:/var/www/$(PROJECT_NAME)/ \
		-v /apps/certs:/etc/nginx/certs  \
		-v /apps/config/:/etc/nginx/vhost.d:ro \
		-v /var/run/docker.sock:/tmp/docker.sock:ro \
		jwilder/nginx-proxy
