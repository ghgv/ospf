#!/bin/bash
sudo python3 clasifier.py &
sudo python3 receiver.py &
sudo python3 ethsend.py  enx7cc2c6453d1f  ff:ff:ff:ff:ff:ff "Hello everybody!" &
sudo iptables -I OUTPUT -p icmp --icmp-type destination-unreachable -j DROP
wait
