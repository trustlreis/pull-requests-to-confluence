#!/bin/bash

# Start the cron service
service cron start

# Tail the cron log to keep the container running
tail -f /var/log/cron.log
