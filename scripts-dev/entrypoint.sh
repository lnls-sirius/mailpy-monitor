#!/bin/bash
set -exu

[[ -f /run/secrets/ALERT_MAIL_PASSWORD ]] &&
    ALERT_MAIL_PASSWORD="$(cat /run/secrets/ALERT_MAIL_PASSWORD)"
[[ -f /run/secrets/ALERT_MAIL_LOGIN ]] &&
    ALERT_MAIL_LOGIN="$(cat /run/secrets/ALERT_MAIL_LOGIN)"

mailpy \
    -p "${ALERT_MAIL_PASSWORD}" \
    --login "${ALERT_MAIL_LOGIN}" \
    --db_url "${MONGODB_URI}"
