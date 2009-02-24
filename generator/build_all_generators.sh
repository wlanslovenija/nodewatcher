#!/bin/bash

# CONFIGURATION
OPENWRT="../openwrt-200901"
GENERATORS=(
  "config-broadcom-2.4 brcm24 brcm-2.4"
  "config-broadcom-2.6 broadcom brcm47xx"
  "config-fonera atheros atheros"
)

# -----------------------------------------------------------

if [ ! -d build ]; then
  mkdir build
  mkdir build/packages
else
  rm -rf build/*
  mkdir build/packages
fi

GENDIR=`pwd`
cd ${OPENWRT}

for i in $(seq 0 $((${#GENERATORS[@]} - 1))); do
  config=`echo -n ${GENERATORS[$i]} | cut -d ' ' -f 1`
  dest=`echo -n ${GENERATORS[$i]} | cut -d ' ' -f 2`
  pkg=`echo -n ${GENERATORS[$i]} | cut -d ' ' -f 3`
  
  echo ">>> Preparing to build ${config}..."
  make distclean > /dev/null 2> /dev/null
  
  echo ">>> Copying image configuration..."
  cp "configs/${config}" .config

  echo ">>> Building image..."
  make >/dev/null 2>/dev/null
  if [ "$?" != "0" ]; then
    echo "!!! Failed to build image for ${config}!"
    exit 1
  fi

  echo ">>> Copying packages..."
  cp -r bin/packages/${pkg} ${GENDIR}/build/packages/${pkg}

  echo ">>> Extracting image builder..."
  ID="$$_$RANDOM"
  mkdir /tmp/ib$ID
  tar xfj bin/*.tar.bz2 -C /tmp/ib$ID
  mv /tmp/ib$ID/OpenWrt* ${GENDIR}/build/imagebuilder.${dest}

  echo ">>> Cleaning up files..."
  rmdir /tmp/ib$ID

  echo ">>> Build completed."
done

echo ">>> All image generators built!"

