#!/bin/bash

set -a
source /tmp/env_vars.sh
set +a

python3 /app/sweeper.py $*
