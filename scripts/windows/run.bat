@echo off

call .\scripts\windows\prepare-env.bat

set FLASK_APP=app
set FLASK_ENV=development

flask run --host=0.0.0.0 --port=%APP_PORT%
