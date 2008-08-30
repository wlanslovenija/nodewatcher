#!/bin/bash

python build_image.py \
  --iface=wl0 \
  --driver=broadcom \
  --port-layout=wrt54gl \
  --node-type=adhoc \
  --password=abc \
  --hostname=node-17 \
  --ip=10.14.0.17 \
  --add-subnet=wl0,10.16.201.160/27,dhcp,olsr \
  --add-iface=wan,eth0.1,dhcp,init \
  --captive-portal \
  --vpn \
  --vpn-username=USERNAME \
  --vpn-password=PASSWORD
