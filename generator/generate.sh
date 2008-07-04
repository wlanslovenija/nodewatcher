#!/bin/bash

python build_image.py \
  --iface=wl0 \
  --driver=broadcom \
  --port-layout=buffalo \
  --node-type=adhoc \
  --password=abc \
  --hostname=node-31 \
  --ip=10.14.0.31 \
  --add-subnet=wl0,10.16.200.160/27,dhcp,olsr \
  --add-iface=wan,eth0.1,dhcp,init \
  --captive-portal \
  --vpn \
  --vpn-username=USERNAME \
  --vpn-password=PASSWORD
