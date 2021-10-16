#!/usr/bin/env sh

. ./scripts/prepare-env-test.sh

export FLASK_APP=app
export FLASK_ENV=development

pip install -e . --quiet --quiet

python3 ./db/wait_db.py
python3 ./db/create_db.py
python3 ./db/init_db.py

pytest
