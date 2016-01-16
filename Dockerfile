FROM default_webapp
MAINTAINER JR Minnaar <jr.minnaar@gmail.com>

# Add a non-privilaged user
RUN adduser --disabled-password --gecos '' --no-create-home webapp && \
    chown -R webapp:webapp /app

RUN chown -R webapp:webapp /env

USER webapp
ENV HOME /app
WORKDIR /app
COPY ./bin/docker-entrypoint.sh /docker-entrypoint.sh
