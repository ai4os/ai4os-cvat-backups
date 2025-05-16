# ai4os-cvat-backups

Implementation for automated backup creation of CVAT projects and annotations using CVAT API.

## components

### backup.py
Python script for creating the backups.

#### Arguments
`--mode [p|a]`

* `p` to back up projects
* `a` to backup annotations

Additional configuration is set by ENV variables:

| ENV variable   | description |
|:----------|:------------|
| `LOG_LEVEL` | debug level; i.e. DEBUG, ERROR, INFO or WARN |
| `CVAT_URL` | full URL to the CVAT instance; e.g., https://0f8d6ec6-2e90-11f0-b9c9-0242ac120004.ifca-deployments.cloud.ai4eosc.eu |
| `CVAT_USERNAME` | CVAT user on whose behalf is the API for creating backups called; preferrably a superuser to be able to backup all the projects |
| `CVAT_PASSWORD` | CVAT user's password |
| `CVAT_BACKUP_DIR` | directory where to store the backup files; e.g., '/cvat-backups' |
| `CVAT_BACKUP_SAVE_IMAGES` | `'true'` or `'false'`, whether to store images along with annotations (when using `backup.py --mode a` |
| `CVAT_BACKUP_REQUEST_TIMEOUT_HOURS` | maximum time in hours to wait for CVAT to prepare a backup |

### sweeper.py
Python script for cleaning old backups according to `${CVAT_BACKUP_TTL}` and `${CVAT_MIN_NUM_BACKUPS}` settings.

Additional configuration is set by ENV variables:

| ENV variable   | description |
|:----------|:------------|
| `LOG_LEVEL` | debug level; i.e. DEBUG, ERROR, INFO or WARN |
| `CVAT_BACKUP_DIR` | directory where to store the backup files; e.g., '/cvat-backups' |
| `CVAT_BACKUP_TTL` | minimum age of backup file in hours; if the age of the backup file exceeds this value and there are more than `${CVAT_MIN_NUM_BACKUPS}` backup files, this backup is deleted by the sweeper |
| `CVAT_MIN_NUM_BACKUPS` | minimum number of backup files to keep regardless of their age (`${CVAT_BACKUP_TTL}`) |

## running locally

### backup.py wrapper
`$ run-locally-backup.sh`

### sweeper.py wrapper
`$ run-locally-sweeper.sh`

## running with docker compose

### additional ENV variables for docker compose

| ENV variable   | description |
|:----------|:------------|
| `LOG_LEVEL` | debug level; i.e. DEBUG, ERROR, INFO or WARN |
| `VERSION` | docker image version |
| `PYTHON_VERSION` | e.g., `'3.9.19'`; python version |
| `NAME` | name of the docker compose project |
| `DOCKER_NAMESPACE` | suffix used in container names |

1. edit the `.env` file and `crontab`
1. `$ docker compose --env-file .env up --build -d`
