#!/usr/bin/env bash
# Copy billmill.org's data from the old box to a new one provisioned by
# ops/deploy.sh, then start caddy and the journal on the new box. Data streams
# through this machine, since the boxes can't ssh to each other.
#
# Safe to rerun; rerun it just before switching DNS to pick up the latest logs
# and databases.
#
# usage: ops/migrate.sh root@<new-ip>
set -euo pipefail

NEW=${1:?usage: $0 root@<new-ip>}
OLD=${OLD:-root@billmill.org}
KEY=$HOME/.ssh/billmill.org.key
ssh_opts=(-i "$KEY" -o ConnectTimeout=10)

# traffic.db is written at :05 past the hour and access.html at :01; don't copy
# them mid-write
minute=$(date -u +%M)
if [ "$minute" -lt 10 ]; then
    echo "it's $minute past the hour, when the cron jobs write; try again after :10" >&2
    exit 1
fi

paths=(
    var/www/html                      # the site, plus goaccess and nba-traffic reports
    srv/journal                       # journal binary and posts.sqlite3
    root/nba-traffic                  # traffic.py
    var/lib/nba-traffic               # traffic history, older than the logs
    var/log/caddy                     # access logs, read by goaccess and traffic.py
    var/lib/caddy/.local/share/caddy  # TLS certificates and ACME account
)

ssh "${ssh_opts[@]}" "$NEW" systemctl stop caddy llimllib-journal

# --no-overwrite-dir keeps the new box's directory permissions
ssh "${ssh_opts[@]}" "$OLD" tar -C / -czf - "${paths[@]}" |
    ssh "${ssh_opts[@]}" "$NEW" tar -C / -xzf - --no-overwrite-dir

ssh "${ssh_opts[@]}" "$NEW" '
    set -euxo pipefail
    chown -R journal:journal /srv/journal
    systemctl restart llimllib-journal
    systemctl enable --now caddy
    systemctl --no-pager status caddy llimllib-journal | grep -E "^●|Active:"
'

ip=${NEW#*@}
cat <<EOF

Copied. Next:
  * install the nba-traffic cron job:
      SERVER=$NEW ~/code/nba0bservable/ops/traffic/install.sh
  * test sites against the new box before switching DNS, e.g.
      curl -sI --resolve billmill.org:443:$ip https://billmill.org/
EOF
