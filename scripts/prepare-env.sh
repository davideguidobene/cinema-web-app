#!/usr/bin/env sh

dot_env_path="./instance/.env"

# Prepare environment
export $(grep -v '^#' "${dot_env_path}" | xargs)

echo "${DOCKER_APP_IMAGE_NAME}"

# TODO
# ? OLD ?
