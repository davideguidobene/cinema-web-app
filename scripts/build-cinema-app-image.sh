#!/usr/bin/env sh

. ./scripts/prepare-env.sh

docker rmi "${DOCKER_APP_IMAGE_NAME}" 2>/dev/null 1>/dev/null

docker build . -t "${DOCKER_APP_IMAGE_NAME}"
