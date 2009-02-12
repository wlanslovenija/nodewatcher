#!/bin/bash

# CONFIGURATION
OPENWRT="../openwrt-200901"
GENERATORS=(
  "config-broadcom-2.4 brcm24"
  "config-broadcom-2.6 broadcom"
  "config-fonera atheros"
)

# -----------------------------------------------------------

if [ ! -d build ]; then
  mkdir build
fi

GENDIR=`pwd`
cd ${OPENWRT}

for i in $(seq 0 $((${#GENERATORS[@]} - 1))); do
  config=`echo -n ${GENERATORS[$i]} | cut -d ' ' -f 1`
  dest=`echo -n ${GENERATORS[$i]} | cut -d ' ' -f 2`
  
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

