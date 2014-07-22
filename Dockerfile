FROM ubuntu:trusty
MAINTAINER Jernej Kos, jernej@kos.mx

# Expose development HTTP port
EXPOSE 8000

# Setup environment variable defaults
ENV PYTHONUNBUFFERED 1

# Update packages
RUN apt-get update

# Install base packages
RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y git python python-dev python-pip build-essential

# Add dependency information
WORKDIR /code
ADD ./packages.txt /code/packages.txt
ADD ./requirements.txt /code/requirements.txt

# Install code dependencies
RUN cat /code/packages.txt | DEBIAN_FRONTEND=noninteractive xargs apt-get --no-install-recommends -y --force-yes install
# Install Python package dependencies (do not use pip install -r here!)
RUN { cat /code/requirements.txt | xargs -n 1 pip install; } || true
