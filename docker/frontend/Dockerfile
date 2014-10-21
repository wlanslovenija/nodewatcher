FROM wlanslovenija/nodewatcher-base

MAINTAINER Jernej Kos <jernej@kos.mx>

EXPOSE 80/tcp

RUN apt-get update -q -q && \
 apt-get install -y uwsgi-plugin-python nginx-full

COPY ./etc /etc

