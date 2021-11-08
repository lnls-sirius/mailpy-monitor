#!/bin/sh
set -exu
AUTHOR="Claudio F. Carneiro <claudiofcarneiro@hotmail.com>"
BRANCH=$(git branch --no-color --show-current)
BUILD_DATE=$(date -I)
BUILD_DATE_RFC339=$(date --rfc-3339=seconds)
COMMIT=$(git rev-parse --short HEAD)
DATE=$(date -I)
REPOSITORY=$(git remote show origin | grep Fetch | awk '{ print $3 }')

docker build \
	--label "org.opencontainers.image.authors='${AUTHOR}'" \
	--label "org.opencontainers.image.created='${BUILD_DATE_RFC339}'" \
	--label "org.opencontainers.image.revision='${COMMIT}'" \
	--label "org.opencontainers.image.source='${REPOSITORY}'" \
	--label "org.opencontainers.image.url='${REPOSITORY}'" \
	--label "org.opencontainers.image.vendor=CNPEM" \
	--label "org.opencontainers.image.version='${COMMIT}-${DATE}'" \
	--label "org.opencontainers.image.description='EPICS Alarm Server'" \
	--label "org.opencontainers.image.title='EPICS Alarm Server'" \
	--tag carneirofc/mailpy-monitor:${COMMIT}-${DATE} \
    .

#Options:
#--add-host list           Add a custom host-to-IP mapping (host:ip)
#--build-arg list          Set build-time variables
#--cache-from strings      Images to consider as cache sources
#--disable-content-trust   Skip image verification (default true)
#-f, --file string             Name of the Dockerfile (Default is 'PATH/Dockerfile')
#--iidfile string          Write the image ID to the file
#--isolation string        Container isolation technology
#--label list              Set metadata for an image
#--network string          Set the networking mode for the RUN instructions during build (default "default")
#--no-cache                Do not use cache when building the image
#-o, --output stringArray      Output destination (format: type=local,dest=path)
#--platform string         Set platform if server is multi-platform capable
#--progress string         Set type of progress output (auto, plain, tty). Use plain to show container output (default "auto")
#--pull                    Always attempt to pull a newer version of the image
#-q, --quiet                   Suppress the build output and print image ID on success
#--secret stringArray      Secret file to expose to the build (only if BuildKit enabled): id=mysecret,src=/local/secret
#--ssh stringArray         SSH agent socket or keys to expose to the build (only if BuildKit enabled) (format: default|<id>[=<socket>|<key>[,<key>]])
#-t, --tag list                Name and optionally a tag in the 'name:tag' format
#--target string           Set the target build stage to build.
