wlan Ljubljana gateway policy daemon
=========================================================================

This daemon can be used to set traffic speed limits to traffic leaving
the gateway via VPN and going towards the wifi nodes (eg. their apparent
download speed).

Usage:
  ./gwpolicyd -i tap0 -p 10.14 

This will shape egress traffic on tap0 interface and will create proper
double hash tables for subnet 10.14.0.0/16, so filter matching operations
will be reduced to two hash table lookups and one filter match.

Supported classifications
=========================================================================

1. IPv4

When performing IPv4 classification, bytes 3 and 4 of an IP address are
used as hash keys.

2. Ethernet

When performing MAC-address bassed classification, bytes 5 and 6 are
used as hash keys.

