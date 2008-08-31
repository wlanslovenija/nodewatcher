#!/bin/bash

python build_image.py \
  --iface=wl0 \
  --driver=broadcom \
  --port-layout=wrt54gl \
  --node-type=adhoc \
  --password=abc \
  --hostname=node-XX \
  --ip=10.14.0.XX \
  --add-subnet=wl0,10.16.20Y.ZZZ/27,dhcp,olsr \
  --add-iface=wan,eth0.1,dhcp,init \
  --captive-portal \
  --vpn \
  --vpn-username=USERNAME \
  --vpn-password=PASSWORD
