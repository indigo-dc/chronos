#!/bin/bash

mkdir /mnt/oneclient
oneclient --no_check_certificate --authentication token /mnt/oneclient

cd /mnt/oneclient/"$ONEDATA_SPACE"/"$ONEDATA_PATH"

curl -s https://raw.githubusercontent.com/indigo-dc/chronos/devel/utilities/upload_job_output/main.py | python

