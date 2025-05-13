#!/usr/bin/env bash

set -a
source .env
set +a

export LOG_LEVEL='INFO'
export CVAT_BACKUP_DIR='./backups'
export CVAT_BACKUP_TTL_HOURS=0
export CVAT_MIN_NUM_BACKUPS=2

./sweeper.py
