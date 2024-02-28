#!/bin/bash

set -euo pipefail

sudo sed -i 's/DNS=.*/DNS=8.8.8.8/g' /etc/systemd/resolved.conf
sudo service systemd-resolved restart
sudo rm -f /etc/resolv.conf
sudo ln -s /run/systemd/resolve/resolv.conf /etc/resolv.conf

