# ZapGo django starter app and deployment setup.
ZapGo's Docker based development and deployment stack for [django](https://www.djangoproject.com/) based on jr-minnaar/dstack.

## Requirements

Internal dependencies:

- [docker-image-factory](https://github.com/zapgo/docker-im): build python wheel packages and create lightweight django application container (app runtime, requirements.txt)

External dependencies:

- [docker-machine](https://docs.docker.com/machine/) for automatic vps creation and deployment
- [nginx-proxy](https://github.com/jwilder/nginx-proxy) for automatic reverse proxying and static file serving.
- [letsencrypt](https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion) for automatic TSL certificates.
- [fabric](http://www.fabfile.org/) for automating tasks locally and on server. ([python3 clone](https://github.com/akaariai/fabric))
- [postgres](http://www.postgresql.org/) everywhere, for both development and deployment

## Getting started
###Initial setup:
1. Install Anaconda for python virtual environment management.
2. Install Fabric in a Python 2.7 virtualenv:

	```
	make fab
	```
3. Create and run python virtual environment from which to manage the deployment:

	```
	conda env create -f etc/fab_environment.yml 
	source activate fab
	```

###Virtual Machine Set-Up:
1. Create the server on Digital Ocean, Google Cloud or AWS:
	```
	fab -f ./etc/server/fabric_tasks.py create_server:provider='digitalocean'
	```
	*When using gcloud, first install gcloud and run gcloud auth login

2. Add the newly created VM to your ssh config file:
	```
	fab -f ./etc/server/fabric_tasks.py create_ssh_config
	```

###Project Deployment:

Ensure that you have a .env file in the root directory with the project settings. Example:

```
PROJECT_NAME=django-starter 
VIRTUAL_ENV=django-starter 
HOST_NAME=starter.zapgo.co
VIRTUAL_HOST=starter.zapgo.co
LETSENCRYPT_EMAIL=*your email*
LETSENCRYPT_HOST=starter.zapgo.co
IMAGE_NAME=zapgo/starter
DJANGO_SECRET=*secret key*
DEBUG=False
```

Update the first line of etc/environment.yml to reflect your chosen virtual environment name (e.g. django-starter).

Create the local virtual environment and static file locations:
```
fab local_setup
```


