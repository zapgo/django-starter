FROM ubuntu

ENV http_proxy 'http://proxy.dcl.tetrapak.com:8080'

RUN apt-get update && apt-get install -y rsync ssh vim wget tree git curl fabric

HOME /Users/canary
USER canary
