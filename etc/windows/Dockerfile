FROM drsync

ENV http_proxy=http://proxy.dcl.tetrapak.com:8080

RUN apt-get update && apt-get install -y rsync ssh

COPY .ssh /root/.ssh
RUN chmod -R 600 /root/.ssh

VOLUME