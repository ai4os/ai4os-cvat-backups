#!/usr/bin/env python

# argument parser
import argparse
parser = argparse.ArgumentParser()
parser.add_argument(
    '--mode',
    choices=['a', 'p'],
    required=True,
    help="Mode of operation: 'a' for annotations, 'p' for projects"
)
args = parser.parse_args()

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

import requests
import sys

from cvat_sdk.api_client import Configuration, ApiClient, exceptions
from datetime import datetime, timedelta
from time import sleep
from urllib.parse import urlparse

#
# ENV VARS -->
#
backup_dir = os.getenv('CVAT_BACKUP_DIR', os.path.join(os.sep, 'cvat-backups'))
os.makedirs(backup_dir, exist_ok=True)
logger.info('backup_dir: %s' % backup_dir)

backup_format = os.getenv('CVAT_BACKUP_FORMAT', 'CVAT for images 1.1')
logger.info('backup_format: %s' % backup_format)

save_images = get_bool_env('CVAT_BACKUP_SAVE_IMAGES', False)
logger.info('save_images: %s' % save_images)

request_timeout = timedelta(hours=int(os.getenv('CVAT_BACKUP_REQUEST_TIMEOUT_HOURS', '1')))
logger.info('request_timeout: %s' % request_timeout)
#
# <-- ENV VARS
#

# Set up an API client
# Read Configuration class docs for more info about parameters and authentication methods
configuration = Configuration(
  host = os.getenv('CVAT_URL'),
  username = os.getenv('CVAT_USERNAME'),
  password = os.getenv('CVAT_PASSWORD'),
)

with ApiClient(configuration) as api_client:

  projects = None
  
  try:
    logger.info('retrieving projects...')
    (data, response) = api_client.projects_api.list()
    assert response.status == 200, response.msg
    projects = data['results']
    logger.info('projects retrieved: %d' % len(projects))
  except exceptions.ApiException as e:
    logger.error('Exception when calling ProjectsApi.list(): %s\n' % e)
    sys.exit(1)

  # backup projects
  for project in projects:
    logger.info('requesting backup of a project: id=%d name=%s' % (project['id'], project['name']))
    project_id = project['id'] # int | A unique integer value identifying this project.
    rq = None
    try:
      if args.mode == 'a':
        (rq, response) = api_client.projects_api.create_dataset_export(
          backup_format,
          project_id,
          save_images=save_images
        )
      if args.mode == 'p':
        (rq, response) = api_client.projects_api.create_backup_export(project_id)
      assert response.status == 202, response.msg
      logger.info('request created: %s' % str(rq))
    except exceptions.ApiException as e:
      logger.error('Exception when calling ProjectsApi.create_dataset_export(): %s\n' % e)

    rq_info = None
    request_time = datetime.now()
    while datetime.now() - request_time < request_timeout:
      try:
        (rq_info, response) = api_client.requests_api.retrieve(rq.rq_id)
        assert response.status == 200, response.msg
        logger.info('request info status: %s' % rq_info.status)
        if rq_info.status.value in {'finished', 'failed'}:
          break
        sleep(10) # retry in 10s
      except exceptions.ApiException as e:
        logger.error('Exception when calling RequestsApi.retrieve(): %s\n' % e)
    assert rq_info
    assert rq_info.status.value == 'finished', rq_info.status.message

    url = rq_info.result_url
    response = requests.get(url, auth=requests.auth.HTTPBasicAuth(configuration.username, configuration.password), stream=True)
    response.raise_for_status()

    # Try to get filename from the 'Content-Disposition' header
    cd = response.headers.get('Content-Disposition')
    if cd and 'filename=' in cd:
      filename = cd.split('filename=')[1].strip('";\' ')
    else:
      # Fallback: extract from URL
      parsed_url = urlparse(url)
      filename = os.path.basename(parsed_url.path) or 'downloaded_file'

    download_filename = os.path.join(backup_dir, filename)

    # Save the file if it does not exist
    if os.path.exists(download_filename):
      logger.info('backup already exists: %s' % download_filename)
      continue

    with open(download_filename, 'wb') as f:
      logger.info('downloading: %s' % rq_info.result_url)
      for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

    logger.info(f"Downloaded as: {download_filename}")
