FROM wlanslovenija/nodewatcher-base

MAINTAINER Jernej Kos <jernej@kos.mx>

EXPOSE 8030/tcp

RUN apt-get update -q -q && \
 apt-get install -y uwsgi-plugin-python

COPY ./etc /etc

