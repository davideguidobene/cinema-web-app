@echo off

call .\scripts\windows\prepare-env.bat

docker rmi %{DOCKER_APP_IMAGE_NAME}% > nul 2>&1

docker build . -t %DOCKER_APP_IMAGE_NAME%
