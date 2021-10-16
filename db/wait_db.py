#!/usr/bin/env python3

import os
import sys
import time
import urllib.parse

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError


# load environment variables
DIALECT = os.getenv("DIALECT")
DB_DEFAULT_USER = os.getenv("DB_DEFAULT_USER")
DB_DEFAULT_DB = os.getenv("DB_DEFAULT_DB")
DB_DEFAULT_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_DEFAULT_PASSWORD"))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# sqlalchemy compliant database url
DB_STRING = f"{DIALECT}://{DB_DEFAULT_USER}:{DB_DEFAULT_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DEFAULT_DB}"


def try_connect(engine, times=20):
    """Tenta di connettersi all'engine (db) times volte"""

    if times <= 0:                                  # numero di tentativi esaurito
        return False

    try:
        conn = engine.connect()                     # prova a connetterti
        return True
    except OperationalError:                        # connessione fallita
        time.sleep(2)                               # attendi 2 secondi
        return try_connect(engine, times-1)         # riprova a connetterti


if __name__ == "__main__":
    engine = create_engine(DB_STRING)

    connected = try_connect(engine, times=20)       # tenta di connetterti al database al più 20 volte

    if not connected:
        print("Connection to database refused", file=sys.stderr)
