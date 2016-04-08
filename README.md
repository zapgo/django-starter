# ZapGo django starter app and deployment setup.
ZapGo's Docker based development and deployment stack for [django](https://www.djangoproject.com/) based on [jr-minnaar/dstack](https://github.com/jr-minnaar/dstack).

## Requirements

Requires [Python](https://www.python.org/), [Docker Toolkit](https://docs.docker.com/), [Anaconda](https://store.continuum.io/cshop/anaconda/) and some other dependancies. Complete, heavy-weight development set up guide for MacOSX can be found [here](https://github.com/jr-minnaar/goeie-hoop).

## Getting started
###Initial setup:
1. Install Anaconda for python virtual environment management.
2. Install Fabric in a Python 2.7 virtual environment:

	```
	make fab
	```
3. Create and run python virtual environment from which to manage the deployment:

	```
	conda env create -f etc/fab_environment.yml 
	```

4. Activate the Fabric virtual environment. All fab commands should be run from here:
	```
	source activate fab
	```

###Virtual Machine Set-Up:
Rapidly launch and setup a server on AWS, Google Cloud Platform or Digital Ocean for running one or multiple projects.

1. Ensure that you have a `/etc/.server.env` file set up with the project settings. Example:

	```
	HOST_NAME=gcloud-starter
	IMAGE_NAME=zapgo/starter
	
	SSH_USERNAME=root
	SSH_PORT=22
	
	DOCKER_COMPOSE_VERSION=1.5.1
	
	DIGITAL_OCEAN_TOKEN=*digital ocean key*
	AWS_ACCESS_KEY_ID=*AWS key*
	AWS_SECRET_ACCESS_KEY=*AWS secret*
	```

2. Create the server on Digital Ocean, Google Cloud or AWS:
	```
	fab -f ./etc/server/fabric_tasks.py 		create_server:provider='digitalocean'
	```
	*When using gcloud, first install gcloud and run gcloud auth login

3. Add the newly created VM to your ssh config file:
	```
	fab -f ./etc/server/fabric_tasks.py create_ssh_config
	```
	
4. Install docker-compose and set up directory structure on server:
	```
	fab -f ./etc/server/fabric_tasks.py install_server_requirements
	```

5. Install the docker-image-factory for updating docker images when python dependancies change:
	```
	fab -f ./etc/server/fabric_tasks.py install_image_factory
	```
	
6. Load nginx and letsencrypt docker containers for automatic reverse proxy and SSL management for all projects running on this VM:
	```
	 fab -f ./etc/server/fabric_tasks.py nginx_ssl_setup
	 ```

###Project Deployment:
This setup is structured so that multiple projects can run alongside each other on the same server in separate docker containers. Here's how to start a new project:

1. Ensure that you have a `.env` file in the root directory with the project settings. Example:

	```
	PROJECT_NAME=django-starter 
	VIRTUAL_ENV=django-starter 
	HOST_NAME=gcloud-starter
	VIRTUAL_HOST=starter.zapgo.co
	
	IMAGE_NAME=zapgo/starter
	
	DJANGO_SECRET=*secret key*
	DEBUG=False
	
	LETSENCRYPT_EMAIL=*your email*
	LETSENCRYPT_HOST=starter.zapgo.co
	```

2. Update the first line of `etc/environment.yml` to reflect your chosen virtual environment name (e.g. django-starter).
	
3. Create the local virtual environment:
	
	```
	fab local_setup
	```

4. Ensure that your  ~/.ssh/config file to map the correct IP address and ssh key. This would have been done automatically if you followed the VM Set-up guide. Here's an example:

	```
	Host gcloud-starter
		HostName 146.148.20.217
		Port 22
		User docker-user
		IdentityFile ~/.docker/machine/machines/gcloud-starter/id_rsa
	```
	
5. Set up a local docker container to run postgresql and create a link to it in `/etc/hosts` for easy local deployent:




