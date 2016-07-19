#!/bin/bash

env

echo "Mounting Onedata Service Space..."

mkdir /mnt/onedata
ONECLIENT_AUTHORIZATION_TOKEN="$ONEDATA_SERVICE_TOKEN" PROVIDER_HOSTNAME="$ONEDATA_PROVIDERS" oneclient /mnt/onedata || exit 1

cd /mnt/onedata/

export UPLOAD_DIR="$ONEDATA_SPACE"/"$ONEDATA_PATH"

rm -rf "$UPLOAD_DIR"/*

curl -s https://raw.githubusercontent.com/indigo-dc/chronos/master/utilities/upload_job_output/main.py | python

echo "Cleaning temporary files"
rm -rf "$UPLOAD_DIR"/*

cd / && umount /mnt/onedata

