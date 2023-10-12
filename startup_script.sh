#!/usr/bin/env bash

declare -p | grep -Ev 'BASHOPTS|BASH_VERSINFO|EUID|PPID|SHELLOPTS|UID' > /container.env
chmod 0644 /etc/cron.d/antibody-ext-cron
touch /var/log/antibody_ext_pipeline.log
crontab /etc/cron.d/antibody-ext-cron
cron

tail -f /dev/null