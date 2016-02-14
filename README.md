# OBITEC |dstack
Docker based development and deployment stack for [django](https://www.djangoproject.com/).
Aims to automate all the boring stuff and let you develop fully production ready from the first line of code.

## Introduction

Component three of the OBITEC stack:
1. [djskel](https://github.com/obitec/djskel): django skeleton app (app source, manage.py)
2. [wheel-factory](https://github.com/jr-minnaar/wheel-factory): build python wheel packages and create lightweight django application container (app runtime, requirements.txt)
3. __dstack__: development and deployment setup (app config, docker-compose.yml, fabric_tasks.py)

Relies on:
- [docker-machine](https://docs.docker.com/machine/) for automatic vps creation and deployment
- [nginx-proxy](https://github.com/jwilder/nginx-proxy) for automatic reverse proxying and static file serving.
- [letsencrypt](https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion) for automatic TSL certificates.
- [fabric](http://www.fabfile.org/) for automating tasks locally and on server. ([python3 clone](https://github.com/akaariai/fabric))
- [cloud-init](https://cloudinit.readthedocs.org/en/latest/) for app host deployments.
- postgres for both development and deployment

Currently developed and tested for [Digital Ocean](https://www.digitalocean.com/).

Attempts to follow the [twelve-factor app](http://12factor.net/) methodology.

## Getting started

### All systems
- https://www.docker.com/products/docker-toolbox
- https://git-scm.com/
- https://www.continuum.io/downloads
- https://www.jetbrains.com/pycharm/ (optional)
- https://www.sublimetext.com/ (optional)


### Windows
- http://cmder.net/ (create shortcut to get quick access)
- Install Git for windows after cmdr and select the "use native commands option"


### Mac
- Follow instructions [here](https://github.com/jr-minnaar/goeie-hoop)


## Testing

```bash
    git clone https://github.com/jr-minnaar/dstack
    cd dstack/etc
    conda env create
```

    Developed by JR Minnaar.
