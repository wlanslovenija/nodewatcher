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
ADD ./requirements-readthedocs.txt /code/requirements-readthedocs.txt
RUN pip install --upgrade pip && \
    sed -i 's/^-r.*$//g' /code/requirements.txt && \
    cat /code/requirements-readthedocs.txt /code/requirements.txt | xargs -n 1 sh -c 'CPLUS_INCLUDE_PATH=/usr/include/gdal C_INCLUDE_PATH=/usr/include/gdal pip install $0 || exit 255'

# Remove unneeded build-time dependencies
RUN apt-get purge python-dev build-essential -y --force-yes && \
    apt-get autoremove -y --force-yes && \
    rm -f /code/packages.txt /code/requirements.txt

# Add the current version of the code (needed for production deployments)
WORKDIR /code
ADD . /code

