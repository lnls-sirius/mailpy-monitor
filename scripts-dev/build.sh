#!/bin/sh
set -exu
AUTHOR="Claudio F. Carneiro <claudiofcarneiro@hotmail.com>"
BRANCH=$(git branch --no-color --show-current)
BUILD_DATE=$(date -I)
BUILD_DATE_RFC339=$(date --rfc-3339=seconds)
COMMIT=$(git rev-parse --short HEAD)
DATE=$(date -I)
REPOSITORY=$(git remote show origin | grep Fetch | awk '{ print $3 }')

sed -i "s|__date__ = .*|__date__ = \"${BUILD_DATE_RFC339}\"|g" src/mailpy/info.py
sed -i "s|__version__ = .*|__version__ = \"${COMMIT}\"|g" src/mailpy/info.py

TAG=carneirofc/mailpy-monitor:${COMMIT}-${DATE}
sed -i "s|.*image:.*|    image: ${TAG}|g" scripts-dev/docker-compose.yml

docker build \
	--label "maintainer='${AUTHOR}'" \
	--label "org.opencontainers.image.authors='${AUTHOR}'" \
	--label "org.opencontainers.image.created='${BUILD_DATE_RFC339}'" \
	--label "org.opencontainers.image.revision='${COMMIT}'" \
	--label "org.opencontainers.image.source='${REPOSITORY}'" \
	--label "org.opencontainers.image.url='${REPOSITORY}'" \
	--label "org.opencontainers.image.vendor=CNPEM" \
	--label "org.opencontainers.image.version='${COMMIT}-${DATE}'" \
	--label "org.opencontainers.image.description='EPICS Alarm Server'" \
	--label "org.opencontainers.image.title='EPICS Alarm Server'" \
    --target mailpy \
	--tag ${TAG} \
	.
