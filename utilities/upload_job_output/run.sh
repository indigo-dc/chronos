#!/bin/bash

env

mkdir /mnt/oneclient
ONECLIENT_AUTHORIZATION_TOKEN="$ONEDATA_SERVICE_TOKEN" PROVIDER_HOSTNAME="$ONEDATA_PROVIDERS" oneclient /mnt/oneclient

cd /mnt/oneclient/"$ONEDATA_SPACE"/"$ONEDATA_PATH"

curl -s https://raw.githubusercontent.com/indigo-dc/chronos/devel/utilities/upload_job_output/main.py | python

umount /mnt/oneclient

