#!/usr/bin/env bash

set -o errexit
set -o nounset
set -o pipefail
if [[ "${TRACE-0}" == "1" ]]; then
    set -o xtrace
fi

BUCKET=$DJANGO_AWS_STORAGE_BUCKET_NAME


# fetch the media files from the s3 bucket specified by:
# the $DJANGO_AWS_STORAGE_BUCKET_NAME environment variable
# the AWS credentials in the file specified in the AWS_SHARED_CREDENTIALS_FILE environment variable
# the AWs config file specified by the AWS_CONFIG_FILE environment variable
aws s3 sync s3://$BUCKET/media/ ./media/