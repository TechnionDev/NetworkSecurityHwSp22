#!/bin/sh

sudo kill $(ps aux | grep "python3 .*httpServer.py" | grep -v grep | awk '{print $2}')
sudo kill $(ps aux | grep "python3 .*dnsServer.py" | grep -v grep | awk '{print $2}')
sudo kill $(ps aux | grep "python3 .*client.py" | grep -v grep | awk '{print $2}')

sudo python3 dnsServer/dnsServer.py > log/dnsOut.txt &
sudo python3 httpServer/httpServer.py > log/httpserverOut.txt &
sudo python3 client/client.py > log/clientOut.txt &
sudo python3 attacker/attacker.py 
