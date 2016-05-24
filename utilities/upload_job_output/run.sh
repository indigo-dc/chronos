#!/bin/bash

oneclient --no_check_certificate --authentication token /mnt/oneclient

curl -s https://raw.githubusercontent.com/indigo-dc/chronos/devel/utilities/upload_job_output/main.py | python

