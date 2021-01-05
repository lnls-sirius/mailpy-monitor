#!/bin/bash
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate
set -x
python run.py -p "$(cat /run/secrets/ALERT_MAIL_PASSWORD)" \
    --login "$(cat /run/secrets/ALERT_MAIL_LOGIN)" \
    --db_url "${MONGODB_URI}"
