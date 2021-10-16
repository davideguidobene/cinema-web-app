#!/usr/bin/env sh

cd /usr/src/cinema-web-app

. ./scripts/prepare-env.sh

pip3 install -e . --quiet --quiet

# python3 ./db/wait_db.py
# python3 ./db/create_db.py
# python3 ./db/init_db.py

export FLASK_APP=app
export FLASK_ENV=development

flask run --host=0.0.0.0 --port="${APP_PORT}"
