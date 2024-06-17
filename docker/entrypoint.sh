#!/bin/bash

# Start the cron service
service cron start

# Creating file if it not exists
touch /var/log/cron.log

# Tail the cron log to keep the container running
tail -f /var/log/cron.log
