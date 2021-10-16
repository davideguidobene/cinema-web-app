#!/usr/bin/env sh

# Launch the web app without restarting and reinitializing database

# Prepare environment
. ./scripts/prepare-env.sh

# Stop running containers
# docker container stop "${DOCKER_DB_CONTAINER_NAME}" 2>/dev/null 1>/dev/null
docker container stop "${DOCKER_APP_CONTAINER_NAME}" 2>/dev/null 1>/dev/null

# Remove old containers and networks
# docker container rm "${DOCKER_DB_CONTAINER_NAME}" 2>/dev/null 1>/dev/null
docker container rm "${DOCKER_APP_CONTAINER_NAME}" 2>/dev/null 1>/dev/null
# docker network rm "${DOCKER_NETWORK_NAME}" 2>/dev/null 1>/dev/null


# Create network
# docker network create --driver bridge "${DOCKER_NETWORK_NAME}"

# Run postgres db
# docker run --name "${DOCKER_DB_CONTAINER_NAME}" \
#            --network "${DOCKER_NETWORK_NAME}" \
#            -e POSTGRES_USER="${DB_DEFAULT_USER}" \
#            -e POSTGRES_PASSWORD="${DB_DEFAULT_PASSWORD}" \
#            -e POSTGRES_DB="${DB_DEFAULT_DB}" \
#            -d -p 5432:"${DB_PORT}" \
#            postgres:alpine

# Run web app
docker run --name "${DOCKER_APP_CONTAINER_NAME}" \
           --network "${DOCKER_NETWORK_NAME}" \
           -v $(pwd):"/usr/src/cinema-web-app" \
           -it \
           -p "${APP_PORT}":"${APP_PORT}" \
           "${DOCKER_APP_IMAGE_NAME}" \
           "/usr/src/cinema-web-app/scripts/entrypoint-fast.sh"
