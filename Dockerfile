FROM wlanslovenija/runit

MAINTAINER Jernej Kos <jernej@kos.mx>

# Update packages
RUN apt-get update -q -q && \
    apt-get install --no-install-recommends -y git python python-dev python-pip build-essential

# Install code dependencies
ADD ./packages.txt /code/packages.txt
RUN cat /code/packages.txt | xargs apt-get --no-install-recommends -y --force-yes install

# Install Python package dependencies (do not use pip install -r here!)
ADD ./requirements.txt /code/requirements.txt
RUN cat /code/requirements.txt | xargs -n 1 pip install

# Remove unneeded build-time dependencies
RUN apt-get purge python-dev build-essential -y --force-yes && \
    apt-get autoremove -y --force-yes && \
    rm -f /code/packages.txt /code/requirements.txt

# Add the current version of the code (needed for production deployments)
WORKDIR /code
ADD . /code

