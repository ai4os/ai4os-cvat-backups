#!/usr/bin/env bash
printenv > /tmp/env_vars.sh
cron && tail -f /var/log/cron.log
