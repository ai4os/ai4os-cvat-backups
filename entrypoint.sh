#!/usr/bin/env bash
printenv > /tmp/env_vars.sh
sed -i -E 's/NOMAD_META_owner_name=(.+)/NOMAD_META_owner_name="\1"/g' /tmp/env_vars.sh
cron && tail -f /var/log/cron.log
