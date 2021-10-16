#!/usr/bin/env sh

. ./scripts/prepare-env.sh

export FLASK_APP=app
export FLASK_ENV=development

flask run --host=0.0.0.0 --port="${APP_PORT}"
