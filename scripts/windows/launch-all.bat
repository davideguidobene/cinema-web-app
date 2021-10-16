@echo off

rem Prepare environment
call .\scripts\windows\prepare-env.bat

rem Stop running containers
docker container stop %DOCKER_DB_CONTAINER_NAME% > nul 2>&1
docker container stop %DOCKER_APP_CONTAINER_NAME% > nul 2>&1

rem Remove old containers and networks
docker container rm %DOCKER_DB_CONTAINER_NAME% > nul 2>&1
docker container rm %DOCKER_APP_CONTAINER_NAME% > nul 2>&1
docker network rm %DOCKER_NETWORK_NAME% > nul 2>&1


rem Create network
docker network create --driver bridge %DOCKER_NETWORK_NAME%

rem Run postgres db
docker run --name %DOCKER_DB_CONTAINER_NAME% ^
           --network %DOCKER_NETWORK_NAME% ^
           -e POSTGRES_USER=%DB_DEFAULT_USER% ^
           -e POSTGRES_PASSWORD=%DB_DEFAULT_PASSWORD% ^
           -e POSTGRES_DB=%DB_DEFAULT_DB% ^
           -d -p 5432:%DB_PORT% ^
           postgres:alpine

rem Run web app
docker run --name %DOCKER_APP_CONTAINER_NAME% ^
           --network %DOCKER_NETWORK_NAME% ^
           -v /d/ProgettoBD/cinema-web-app:"/usr/src/cinema-web-app" ^
           -it ^
           -p %APP_PORT%:%APP_PORT% ^
           %DOCKER_APP_IMAGE_NAME% ^
           "/usr/src/cinema-web-app/scripts/entrypoint.sh"

::.\scripts\windows\launch-all.bat
