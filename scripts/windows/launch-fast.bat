@echo off


rem Prepare environment
call .\scripts\windows\prepare-env.bat

rem Stop running containers
REM docker container stop %DOCKER_DB_CONTAINER_NAME% > nul 2>&1
docker container stop %DOCKER_APP_CONTAINER_NAME% > nul 2>&1

rem Remove old containers and networks
REM docker container rm %DOCKER_DB_CONTAINER_NAME% > nul 2>&1
docker container rm %DOCKER_APP_CONTAINER_NAME% > nul 2>&1
REM docker network rm %DOCKER_NETWORK_NAME% > nul 2>&1


rem Create network
REM docker network create --driver bridge %DOCKER_NETWORK_NAME%

rem Run postgres db
REM docker run --name %DOCKER_DB_CONTAINER_NAME% ^
REM            --network %DOCKER_NETWORK_NAME% ^
REM            -e POSTGRES_USER=%DB_DEFAULT_USER% ^
REM            -e POSTGRES_PASSWORD=%DB_DEFAULT_PASSWORD% ^
REM            -e POSTGRES_DB=%DB_DEFAULT_DB% ^
REM            -d -p 5432:%DB_PORT% ^
REM            postgres:alpine

rem Run web app
docker run --name %DOCKER_APP_CONTAINER_NAME% ^
           --network %DOCKER_NETWORK_NAME% ^
           -v /d/ProgettoBD/cinema-web-app:"/usr/src/cinema-web-app" ^
           -it ^
           -p %APP_PORT%:%APP_PORT% ^
           %DOCKER_APP_IMAGE_NAME% ^
           "/usr/src/cinema-web-app/scripts/entrypoint-fast.sh"
