FROM wlanslovenija/runit

MAINTAINER Jernej Kos <jernej@kos.mx>

ADD . /code

RUN apt-get update -q -q && \
 apt-get install --no-install-recommends -y git python python-dev python-pip build-essential && \
 cat /code/packages.txt | xargs apt-get --no-install-recommends -y --force-yes install && \
 { { cat /code/requirements.txt | xargs -n 1 pip install; } || true; } && \
 apt-get purge git python-dev build-essential -y --force-yes && \
 apt-get autoremove -y --force-yes

