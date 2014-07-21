FROM ubuntu:trusty
MAINTAINER Jernej Kos, jernej@kos.mx

# Expose development HTTP port
EXPOSE 8000

# Add snapshot of current code
WORKDIR /code
ADD . /code

# Setup environment variable defaults
ENV PYTHONUNBUFFERED 1

# Update packages
RUN apt-get update

# Install base packages
RUN DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y git python python-dev python-pip build-essential

# Install code dependencies
RUN cat /code/packages.txt | DEBIAN_FRONTEND=noninteractive xargs apt-get --no-install-recommends -y --force-yes install
# Install Python package dependencies (do not use pip install -r here!)
RUN { cat /code/requirements.txt | xargs -n 1 pip install; } || true
