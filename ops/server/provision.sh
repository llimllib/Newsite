#!/usr/bin/env bash
# Provision a Debian 13 (trixie) box to serve billmill.org. Run as root from
# /root/ops by ops/deploy.sh; safe to rerun.
set -euxo pipefail

OPS=/root/ops
export DEBIAN_FRONTEND=noninteractive

# apt's daily jobs run soon after boot; wait for their lock instead of failing
apt-get() { command apt-get -o DPkg::Lock::Timeout=600 "$@"; }

apt-get update
apt-get -y upgrade
apt-get install -y \
    apt-transport-https \
    curl \
    cron \
    debian-archive-keyring \
    debian-keyring \
    gpg \
    goaccess \
    python3 \
    rsync \
    sqlite3 \
    unattended-upgrades

# 1GB of swap; the box only has 1GB of RAM
if [ ! -f /swapfile ]; then
    fallocate -l 1G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    echo '/swapfile none swap sw 0 0' >>/etc/fstab
fi
swapon --show | grep -q /swapfile || swapon /swapfile

# install security updates daily, and reboot for them when needed
install -m 644 "$OPS/unattended-upgrades.conf" /etc/apt/apt.conf.d/52unattended-upgrades-local
cat >/etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF

# key-only ssh. Validate before reloading so a bad config can't lock us out
install -m 644 "$OPS/sshd.conf" /etc/ssh/sshd_config.d/10-billmill.conf
sshd -t
systemctl reload ssh

# caddy, from its official repo: https://caddyserver.com/docs/install#debian-ubuntu-raspbian
if [ ! -f /usr/share/keyrings/caddy-stable-archive-keyring.gpg ]; then
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' |
        gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' \
        >/etc/apt/sources.list.d/caddy-stable.list
    chmod o+r /usr/share/keyrings/caddy-stable-archive-keyring.gpg /etc/apt/sources.list.d/caddy-stable.list
    apt-get update
fi
apt-get install -y caddy

# tailscale, from its official repo
if [ ! -f /usr/share/keyrings/tailscale-archive-keyring.gpg ]; then
    curl -fsSL https://pkgs.tailscale.com/stable/debian/trixie.noarmor.gpg \
        >/usr/share/keyrings/tailscale-archive-keyring.gpg
    curl -fsSL https://pkgs.tailscale.com/stable/debian/trixie.tailscale-keyring.list \
        >/etc/apt/sources.list.d/tailscale.list
    apt-get update
fi
apt-get install -y tailscale
if tailscale status >/dev/null 2>&1; then
    tailscale set --auto-update
fi

# the static site, deployed by `make deploy`
mkdir -p /var/www/html/static

# the journal: an archive of old posts, served by a Go binary that
# ops/migrate.sh copies into /srv/journal
id journal >/dev/null 2>&1 || useradd --system --no-create-home --shell /usr/sbin/nologin journal
mkdir -p /srv/journal
chown -R journal:journal /srv/journal
install -m 644 "$OPS/llimllib-journal.service" /etc/systemd/system/llimllib-journal.service
systemctl daemon-reload
systemctl enable llimllib-journal
if [ -x /srv/journal/journal ]; then
    systemctl restart llimllib-journal
fi

# hourly traffic report at billmill.org/static/access.html. nba-traffic's cron
# job is installed by nba0bservable's ops/traffic/install.sh
install -m 644 "$OPS/goaccess.cron" /etc/cron.d/goaccess

# Caddy config. Until ops/migrate.sh has copied over the old box's
# certificates, keep caddy stopped: DNS still points at the old box, so it would
# fail ACME challenges over and over
install -m 644 "$OPS/Caddyfile" /etc/caddy/Caddyfile
caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
if [ -d /var/lib/caddy/.local/share/caddy/certificates ]; then
    systemctl enable caddy
    systemctl reload-or-restart caddy
else
    systemctl disable --now caddy
    echo "no caddy certificates yet; caddy is stopped until ops/migrate.sh runs"
fi
