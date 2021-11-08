#!/bin/bash
set -exu
collections="conditions groups entries"

CONNECTION_OPTS="authSource=admin"
MONGODB_CONNECTION_STRING="mongodb://${MONGO_INITDB_ROOT_USERNAME}:${MONGO_INITDB_ROOT_PASSWORD}@localhost:27017/${MONGO_INITDB_DATABASE}?${CONNECTION_OPTS}"

function import_collection {
    _collection=$1
    mongoimport \
        ${MONGODB_CONNECTION_STRING} \
        --collection ${_collection} \
        /mailpy-db-init-data/${_collection}.json \
        --jsonArray
}

for c in ${collections}; do
    import_collection $c
done
