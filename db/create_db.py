#!/usr/bin/env python3

import os
import urllib.parse

from sqlalchemy import create_engine


# load environment variables
DIALECT = os.getenv("DIALECT")
DB_DEFAULT_USER = os.getenv("DB_DEFAULT_USER")
DB_DEFAULT_DB = os.getenv("DB_DEFAULT_DB")
DB_DEFAULT_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_DEFAULT_PASSWORD"))
DB_APP_USER = os.getenv("DB_APP_USER")
DB_APP_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_APP_PASSWORD"))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# sqlalchemy compliant database url
DB_STRING = f"{DIALECT}://{DB_DEFAULT_USER}:{DB_DEFAULT_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DEFAULT_DB}"


def create_database(db_name, role=None, password=None):
    """Crea il database db_name e opzionalmente un ruolo admin con password"""

    # crea engine configurato correttamente per la creazione di altri database
    db = create_engine(DB_STRING, isolation_level='AUTOCOMMIT', pool_pre_ping=True, echo=False)

    # crea database db_name
    with db.connect() as conn:
        conn.execute(f"CREATE DATABASE {db_name}")

        if role and password:
            conn.execute(f"CREATE ROLE {role} WITH LOGIN ENCRYPTED PASSWORD '{password}' CREATEROLE")


if __name__ == "__main__":
    # crea database usando valori delle variabili d'ambiente
    create_database(DB_NAME, DB_APP_USER, DB_APP_PASSWORD)
