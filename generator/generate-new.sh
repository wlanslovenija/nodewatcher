#!/bin/bash

python build_image.py \
  --iface=ath0 \
  --iface-lan= \
  --channel=8 \
  --openwrt-version=new \
  --arch=mips \
  --driver=atheros \
  --port-layout=fonera \
  --node-type=adhoc \
  --password=abc \
  --hostname=xxx \
  --ip=10.14.x.y \
  --add-subnet=ath0,10.16.2xx.yyy/27,dhcp,olsr \
  --add-iface=wan,eth0,dhcp,init \
  --captive-portal \
  --vpn \
  --vpn-username=xxx \
  --vpn-password=yyy \
  --imagebuilder-dir=imagebuilder.atheros
