FROM tozd/runit:ubuntu-xenial

MAINTAINER Jernej Kos <jernej@kos.mx>

# Update packages
RUN apt-get update -q -q && \
    apt-get install --no-install-recommends -y git python python-dev python-pip python-setuptools build-essential

# Install code dependencies
ADD ./packages.txt /code/packages.txt
RUN cat /code/packages.txt | xargs apt-get --no-install-recommends -y install && \
    chmod 4755 /usr/bin/fping && \
    chmod 4755 /usr/bin/fping6

# Install Python package dependencies (do not use pip install -r here!)
ADD ./requirements.txt /code/requirements.txt
ADD ./requirements-readthedocs.txt /code/requirements-readthedocs.txt
RUN pip install --upgrade --force-reinstall pip six requests && \
    sed -i 's/^-r.*$//g' /code/requirements.txt && \
    cat /code/requirements-readthedocs.txt /code/requirements.txt | xargs -n 1 sh -c 'CPLUS_INCLUDE_PATH=/usr/include/gdal C_INCLUDE_PATH=/usr/include/gdal pip install $0 || exit 255'

# Remove unneeded build-time dependencies
RUN apt-get purge python-dev build-essential -y && \
    apt-get autoremove -y && \
    rm -f /code/packages.txt /code/requirements.txt

# Add the current version of the code (needed for production deployments)
WORKDIR /code
ADD . /code

