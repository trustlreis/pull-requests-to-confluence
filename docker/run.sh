#!/bin/bash
cd /app
/usr/local/bin/python main.py >> /var/log/cron.log 2>&1