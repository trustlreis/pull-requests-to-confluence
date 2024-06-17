# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create a working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies for cron
RUN apt-get update && apt-get install -y cron

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the crontab file into the cron.d directory
COPY docker/run.sh /usr/local/bin/fetch_pull_requests
COPY docker/crontab /etc/cron.d/fetch_pull_requests

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/fetch_pull_requests
RUN chmod 0755 /usr/local/bin/fetch_pull_requests

# Apply the cron job
RUN crontab /etc/cron.d/fetch_pull_requests

# Create the entrypoint script
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Run the command on container startup
CMD ["/entrypoint.sh"]
