#!/bin/bash
set -exu

# Enable TLS is ALERT_MAIL_TLS is defined !
[[ ! -z ${MAIL_SERVER_TLS} ]] && \
    [[ ${MAIL_SERVER_TLS} != "True" ]] && \
    [[ ${MAIL_SERVER_TLS} != "False" ]] && echo 'MAIL_SERVER_TLS requires True/False' && exit 1


MAIL_TLS=$([[ ${MAIL_SERVER_TLS} == "True" ]] && echo "--tls" || echo "")


# Load docker secrets
[[ -f /run/secrets/ALERT_MAIL_PASSWORD ]] &&
    MAIL_CLIENT_PASSWORD="$(cat /run/secrets/ALERT_MAIL_PASSWORD)"

[[ -f /run/secrets/ALERT_MAIL_LOGIN ]] &&
    MAIL_CLIENT_LOGIN="$(cat /run/secrets/ALERT_MAIL_LOGIN)"

mailpy \
    -p "${MAIL_CLIENT_PASSWORD}" \
    --login "${MAIL_CLIENT_LOGIN}" \
    --db_url "${MONGODB_URI}" \
    --mail-server-port ${MAIL_SERVER_PORT} \
    --mail-server-host ${MAIL_SERVER_HOST} \
    "${MAIL_TLS}"

