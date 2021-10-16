@echo off

call .\scripts\windows\prepare-env.bat

set FLASK_APP=app
set FLASK_ENV=development

pip install -e . --quiet --quiet

pytest
