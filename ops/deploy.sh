#!/usr/bin/env bash

# TODO:
# * wait on creation of the machine ✅
# * get caddy installed ✅
# * get limbos running ✅
#    * python 3.8.5 is already present on the image as `python3`
#    * install limbo ✅
#    * need systemd init scripts
#       * this looks maybe helpful: https://github.com/torfsen/python-systemd-tutorial
# * do DNS stuff automatically so we could redeploy?
#    * do I care about a redeploy story?
#       * ugh not rn
# * reboot after install?


set -euxo pipefail

doctl auth init -t $DO_AUTH_TOKEN
if doctl compute droplet list -o json | jq '.[] | select(.name|test("^billmill.org"))'; then
    echo "Creating billmill.org"
    # to show ssh keys:
    # doctl compute ssh-key list
    doctl compute droplet create billmill.org \
        --size s-1vcpu-1gb \
        --image ubuntu-20-04-x64 \
        --region nyc1 \
        --ssh-keys 2a:29:e7:54:eb:e1:84:8a:1a:b4:7c:55:f6:48:28:15 \
        --wait
        # enable?
        # --enable-backups
fi

# once it starts up, should be able to connect with:
# https://caddyserver.com/docs/install#debian-ubuntu-raspbian
doctl compute ssh billmill.org --ssh-command "apt update && \
apt install -y debian-keyring debian-archive-keyring apt-transport-https && \
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | apt-key add - && \
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee -a /etc/apt/sources.list.d/caddy-stable.list && \
apt update &&  \
apt install \
    caddy \
    python3-pip && \
pip3 install limbo && \
mkdir /var/www/html # the default caddy dir to deploy HTML into
"
