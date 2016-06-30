#!/bin/bash

env

mkdir /mnt/onedata
ONECLIENT_AUTHORIZATION_TOKEN="$ONEDATA_SERVICE_TOKEN" PROVIDER_HOSTNAME="$ONEDATA_PROVIDERS" oneclient /mnt/onedata

cd /mnt/onedata/

export UPLOAD_DIR="$ONEDATA_SPACE"/"$ONEDATA_PATH"

curl -s https://raw.githubusercontent.com/indigo-dc/chronos/devel/utilities/upload_job_output/main.py | python

cd / && umount /mnt/onedata

