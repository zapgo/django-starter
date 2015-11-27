FROM kmaginary/base:miniconda
MAINTAINER JR Minnaar <jr.minnaar@gmail.com>

# Add a non-privilaged user
RUN adduser --disabled-password --gecos '' webapp && \
    chown -R webapp:webapp /home/webapp

#VOLUME /home/webapp/.cache/pip/:rw /home/webapp/.conda/envs/.pkgs/:rw

USER webapp
ENV HOME /home/webapp
WORKDIR /home/webapp

COPY environment.yml $HOME/
RUN conda env create

COPY requirements.txt $HOME/
RUN pip install -r requirements.txt

COPY ./bin/docker-entrypoint.sh /home/webapp/docker-entrypoint.sh