ARG PYTHON_VERSION

# Stage 1: Base build stage
FROM python:${PYTHON_VERSION}-slim AS builder

# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install cron
RUN apt-get update && \
    apt-get install -y cron

# Set the working directory
WORKDIR /app

# Copy the cron job file into the container
COPY backup.py /app/backup.py
COPY backup.sh /app/backup.sh
COPY sweeper.py /app/sweeper.py
COPY requirements.txt /app/requirements.txt
COPY crontab /etc/cron.d/cvat-backups
COPY entrypoint.sh /entrypoint.sh

# Upgrade pip and install dependencies
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set permissions
RUN chmod 0644 /etc/cron.d/cvat-backups && \
    chmod +x /entrypoint.sh

# Apply the cron job
RUN crontab /etc/cron.d/cvat-backups

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

ENTRYPOINT ["/entrypoint.sh"]
