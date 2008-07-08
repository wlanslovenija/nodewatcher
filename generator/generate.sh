#!/bin/bash

python build_image.py \
  --iface=wl0 \
  --driver=broadcom \
  --port-layout=wrt54gl \
  --node-type=adhoc \
  --password=abc \
  --hostname=node-XY \
  --ip=10.14.0.XY \
  --add-subnet=wl0,10.16.20Z.ZZZ/27,dhcp,olsr \
  --add-iface=wan,eth0.1,dhcp,init \
  --captive-portal \
  --vpn \
  --vpn-username=USERNAME \
  --vpn-password=PASSWORD
