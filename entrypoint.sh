#!/usr/bin/env bash
# retrieve env vars and quote values containing space
printenv | while IFS='=' read -r k v; do [[ "$v" == *[[:space:]]* ]] && echo "$k=\"$v\"" || echo "$k=$v"; done > /tmp/env_vars.sh
cron && tail -f /var/log/cron.log
