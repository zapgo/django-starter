# ZapGo django starter app and docker deployment setup.
ZapGo's Docker based development and deployment stack for [django](https://www.djangoproject.com/) based on jr-minnaar/dstack.

## Requirements
  - [docker-image-factory](https://github.com/zapgo/docker-im): build python wheel packages and create lightweight django application container (app runtime, requirements.txt)

Relies on:
- [docker-machine](https://docs.docker.com/machine/) for automatic vps creation and deployment
- [nginx-proxy](https://github.com/jwilder/nginx-proxy) for automatic reverse proxying and static file serving.
- [letsencrypt](https://github.com/JrCs/docker-letsencrypt-nginx-proxy-companion) for automatic TSL certificates.
- [fabric](http://www.fabfile.org/) for automating tasks locally and on server. ([python3 clone](https://github.com/akaariai/fabric))
- [cloud-init](https://cloudinit.readthedocs.org/en/latest/) for app host deployments.
- postgres everywhere, for both development and deployment

## Getting started
  coming soon
