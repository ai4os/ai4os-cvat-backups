#!/usr/bin/env bash

set -a
source .env
set +a

export CVAT_BACKUP_DIR='./backups'

./backup.py $*
