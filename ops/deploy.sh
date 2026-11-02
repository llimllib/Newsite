#!/usr/bin/env bash
# Create (if missing) and provision the billmill droplet. Safe to rerun: each
# piece of infrastructure is only created if it doesn't exist, and
# server/provision.sh is idempotent.
#
# Requires an authenticated doctl and jq. After the first run, copy data over
# with ops/migrate.sh.
set -euo pipefail

NAME=billmill
REGION=nyc3
SIZE=s-1vcpu-1gb
IMAGE=debian-13-x64
KEY=$HOME/.ssh/billmill.org.key
OPS=$(cd "$(dirname "$0")" && pwd)

# DigitalOcean identifies ssh keys by their md5 fingerprint
fingerprint=$(ssh-keygen -E md5 -lf "$KEY.pub" | awk '{print $2}' | sed 's/^MD5://')
if ! doctl compute ssh-key list --format FingerPrint --no-header | grep -qx "$fingerprint"; then
    echo "importing ssh key $KEY.pub"
    doctl compute ssh-key import billmill.org --public-key-file "$KEY.pub"
fi

droplet_id() {
    doctl compute droplet list -o json | jq -r --arg name "$NAME" '.[] | select(.name == $name) | .id'
}

id=$(droplet_id)
if [ -z "$id" ]; then
    echo "creating droplet $NAME"
    doctl compute droplet create "$NAME" \
        --image "$IMAGE" \
        --size "$SIZE" \
        --region "$REGION" \
        --ssh-keys "$fingerprint" \
        --tag-names "$NAME" \
        --enable-backups \
        --enable-monitoring \
        --wait
    id=$(droplet_id)
fi

# The reserved IP is what DNS points at, so a future rebuild only needs the IP
# reassigned
reserved_ip=$(doctl compute reserved-ip list -o json |
    jq -r --argjson id "$id" '.[] | select(.droplet.id == $id) | .ip')
if [ -z "$reserved_ip" ]; then
    echo "creating reserved IP"
    reserved_ip=$(doctl compute reserved-ip create --droplet-id "$id" --format IP --no-header)
fi

# Cloud firewall, applied by tag. Tailscale works without inbound 41641, but
# opening it allows direct connections instead of relays
if ! doctl compute firewall list -o json | jq -e --arg name "$NAME" '.[] | select(.name == $name)' >/dev/null; then
    echo "creating firewall $NAME"
    any="address:0.0.0.0/0,address:::/0"
    doctl compute firewall create \
        --name "$NAME" \
        --tag-names "$NAME" \
        --inbound-rules "protocol:tcp,ports:22,$any protocol:tcp,ports:80,$any protocol:tcp,ports:443,$any protocol:udp,ports:443,$any protocol:udp,ports:41641,$any protocol:icmp,$any" \
        --outbound-rules "protocol:tcp,ports:all,$any protocol:udp,ports:all,$any protocol:icmp,$any" \
        >/dev/null
fi

# provision over the droplet's own IP; the reserved IP can take a moment to
# start routing
ip=$(doctl compute droplet get "$id" --format PublicIPv4 --no-header)
ssh_opts=(-i "$KEY" -o StrictHostKeyChecking=accept-new -o ConnectTimeout=5)

echo "waiting for ssh on $ip"
until ssh "${ssh_opts[@]}" "root@$ip" true 2>/dev/null; do sleep 5; done

rsync -az -e "ssh ${ssh_opts[*]}" \
    "$OPS/Caddyfile" "$OPS/server/" "root@$ip:/root/ops/"
ssh "${ssh_opts[@]}" "root@$ip" bash /root/ops/provision.sh

cat <<EOF

droplet:     $NAME ($id)
ip:          $ip
reserved ip: $reserved_ip

If this is a new box:
  * join the tailnet: ssh root@$ip tailscale up --hostname=$NAME
  * copy data over:   ops/migrate.sh root@$ip
EOF
