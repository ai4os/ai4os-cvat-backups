#!/usr/bin/env python

import logging
import os

log_level = os.getenv('LOG_LEVEL', 'INFO')
log_level = getattr(logging, log_level.upper(), logging.INFO)

def get_bool_env(var_name: str, default: bool = False) -> bool:
    val = os.getenv(var_name, str(default)).lower()
    return val in ('1', 'true', 'yes', 'on')

import pathlib
script_name = pathlib.Path(__file__).name

# Create and configure logger
logger = logging.getLogger(script_name)
logger.setLevel(log_level)

# Create console handler
console_handler = logging.StreamHandler()

# Create formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)

from datetime import datetime, timedelta

import os
import re

backup_dir = os.getenv('CVAT_BACKUP_DIR', os.path.join(os.sep, 'cvat-backups'))
logger.info('backup_dir: %s' % backup_dir)

min_num_backups = int(os.getenv('CVAT_MIN_NUM_BACKUPS', '3'))
logger.info('min_num_backups: %s' % min_num_backups)

pattern = re.compile(r'^project_.+_backup_(?P<year>\d{4})_(?P<month>\d{2})_(?P<day>\d{2})_(?P<hour>\d{2})_(?P<minute>\d{2})_(?P<second>\d{2})\.zip$')  # Example: project_project1_backup_2025_05_12_09_26_48.zip

backup_files = [os.path.join(backup_dir, f) for f in os.listdir(backup_dir) if pattern.match(f)]
logger.debug('backup_files: %s' % backup_files)

def get_datetime(filename):
  basename = os.path.basename(filename)
  match = re.search(pattern, basename)
  if not match:
    logger.warn('filename does not match the project_${project_name}_backup_YYYY_MM_DD_HH_mm_ss pattern: %s' % filename)
    return None
  date_components = match.groupdict()
  date_components = {k: int(v) for k,v in date_components.items()}
  missing = {'year', 'month', 'day', 'hour', 'minute', 'second'} - date_components.keys()
  if len(missing) > 0:
    logger.warn('missing date components in %s: %s' % (filename, missing))
    return None
  dt = datetime(
    date_components['year'],
    date_components['month'],
    date_components['day'],
    date_components['hour'],
    date_components['minute'],
    date_components['second']
  )
  return dt

# group files by project name
grouped_backups = {}
for f in backup_files:
  k = os.path.basename(f)
  m = re.search(r'project_([^_]+)', k)
  if m and m.groups():
    k = m.group(1)
  else:
    logger.warning('could not parse project name in %s, skipping file' % k)
    continue
  if k not in grouped_backups.keys():
    grouped_backups[k] = []
  grouped_backups[k].append(f)
logger.debug('grouped_backups: %s' % grouped_backups)

# maximum age of a backup
backup_ttl = int(os.getenv('CVAT_BACKUP_TTL_HOURS', '24'))
backup_ttl = timedelta(hours=backup_ttl)
logger.info('backup_ttl: %s' % backup_ttl)

# current time
now = datetime.now()
logger.info('now: %s' % now)

# loop project backups
for project, backups in grouped_backups.items():
  logger.debug('project: %s' % project)
  # sort backups by date from the oldest to the newest
  backups = [{'file': filename, 'dt': get_datetime(filename)} for filename in backups]
  backups = sorted(backups, key=lambda k: k['dt'], reverse=False) # oldest first
  logger.debug('backups: %s' % backups)
  while len(backups) > min_num_backups:
    backup = backups[0]
    logger.debug('backup: %s' % backup)
    # compute the age of the backup
    backup_age = now - backup['dt']
    logger.debug('backup age: %s' % backup_age)
    # delete old backups
    if backup_age > backup_ttl:
      logger.info('deleting: %s' % backup['file'])
      os.remove(backup['file'])
      logger.info('file has been deleted: %s' % backup['file'])
      backups = backups[1:]
    else:
      # there are no old backups for deleting
      break

