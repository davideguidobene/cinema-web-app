"""
Modulo contenente lo schema della base di dati espresso secondo la sintassi di sqlalchemy.
Inoltre contiene alcune funzioni di utlità prettamente riguardanti il database.
"""

import os
import urllib
from enum import Enum

from flask_login import UserMixin
from sqlalchemy import create_engine, MetaData, Table, Column, ForeignKey
from sqlalchemy.types import Integer, Float, String, Date, DateTime, Boolean, Text


# carica variabili d'ambiente
DIALECT = os.getenv("DIALECT")
DB_APP_USER = os.getenv("DB_APP_USER")
DB_APP_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_APP_PASSWORD"))
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

# url database
DB_STRING = f"{DIALECT}://{DB_APP_USER}:{DB_APP_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


db = create_engine(DB_STRING, pool_pre_ping=True, echo=False)   # istanza dell'engine sqlachemy

metadata = MetaData(db)                                         # metadati per descrivere database


# tabella User
user_table = Table('User', metadata,
    Column('username', String, primary_key=True),
    Column('email', String, unique=True, nullable=False),
    Column('password', String, nullable=False),
    Column('name', String, nullable=False),
    Column('surname', String, nullable=False),
    Column('birthdate', Date, nullable=False),
    Column('registrationDate', Date, nullable=False),
    Column('isOperator', Boolean, nullable=False)
)

# tabella Movie
movie_table = Table('Movie', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String, nullable=False),
    Column('director', Integer, ForeignKey('CastMember.id'), nullable=False),
    Column('plot', Text, nullable=False),
    Column('duration', Integer, nullable=False),
    Column('genre', String, ForeignKey('Genre.name'), nullable=False),
    Column('nation', String, ForeignKey('Nation.name'), nullable=False),
    Column('releaseDate', Date, nullable=False),
    Column('poster', String, nullable=False)
)

# tabella Genre
genre_table = Table('Genre', metadata,
    Column('name', String, primary_key=True)
)

# tabella Nation
nation_table = Table('Nation', metadata,
    Column('name', String, primary_key=True),
)

# tabella CastMember
cast_member_table = Table('CastMember', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, nullable=False),
    Column('surname', String, nullable=False)
)

# tabella ActorMovie
actor_movie_table = Table('ActorMovie', metadata,
    Column('movie', Integer, ForeignKey('Movie.id'), primary_key=True),
    Column('actor', Integer, ForeignKey('CastMember.id'), primary_key=True)
)

# tabella PaymentCircuit
payment_circuit_table = Table('PaymentCircuit', metadata,
    Column('name', String, primary_key=True)
)

# tabella PaymentMethod
payment_method_table = Table('PaymentMethod', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('ownerName', String, nullable=False),
    Column('user', String, ForeignKey('User.username'), nullable=False),
    Column('cardNumber', String, nullable=False),
    Column('expirationDate', Date, nullable=False),
    Column('paymentCircuit', String, ForeignKey('PaymentCircuit.name'), nullable=False),
    Column('isActive', Boolean, nullable=False)
)

# tabella Purchase
purchase_table = Table('Purchase', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('projection', Integer, ForeignKey('Projection.id'), nullable=False),
    Column('total', Float, nullable=False),
    Column('purchaseDatetime', DateTime, nullable=False),
    Column('paymentMethod', Integer, ForeignKey('PaymentMethod.id'), nullable=False)
)

# tabella Ticket
ticket_table = Table('Ticket', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('row', Integer, nullable=False),
    Column('column', Integer, nullable=False),
    Column('purchase', Integer, ForeignKey('Purchase.id'), nullable=False)
)

# tabella Room
room_table = Table('Room', metadata,
    Column('name', String, primary_key=True),
    Column('numberOfRows', Integer, nullable=False),
    Column('numberOfColumns', Integer, nullable=False),
    Column('screenSize', Integer, nullable=False)
)

# tabella Projection
projection_table = Table('Projection', metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('movie', Integer, ForeignKey('Movie.id'), nullable=False),
    Column('room', String, ForeignKey('Room.name'), nullable=False),
    Column('datetime', DateTime, nullable=False),
    Column('price', Float, nullable=False)
)


def get_db():
    """Restituisce il database engine"""

    return db


def close_db():
    """Chiude il database engine, rilasciando le risorse"""

    db.dispose()                                # chiude l'engine rilasciando le risorse


class Role(Enum):
    """Enum che identifica i ruoli del database"""
    WEBAPP = DB_APP_USER
    CLIENT = 'client'
    OPERATOR = 'operator'


def connect_as(role):
    """Restituisce una connessione al database, impostando il ruolo opportunamente

    Args:
        role (Role): ruolo con cui connettersi

    Returns:
        conn: oggetto che modella la connessione al database
    """

    # valida ruolo
    if role not in [ Role.WEBAPP, Role.CLIENT, Role.OPERATOR ]:
        raise ValueError(f'Invalid role: {role}')

    conn = db.connect()                                             # connessione al database
    conn.execute(f'SET ROLE {role.name}; COMMIT;')                  # impostazione del ruolo
    return conn


def init_db():
    """Inizializza il database"""

    metadata.drop_all(db)                       # elimina tutte le tabelle dello schema
    metadata.create_all(db)                     # crea tutte le tabelle dello schema


def get_table_names():
    """Restituisce l'elenco dei nomi delle tabelle

    Returns:
        list: elenco nomi delle tabelle
    """

    return db.table_names()


def get_table_dictionary():
    """Restituisce un dizionario (key:nome_tablla, value:tabella)

    Returns:
        dict: dizionario tra nomi tabelle e tabelle vere e proprie
    """

    return metadata.tables


def init_app(app):
    """Inizializza l'applicazione Flask"""

    app.teardown_appcontext(close_db)           # chiude il database alla chiusura dell'app


class User(UserMixin):
    """Classe User necessaria per Flask-Login"""

    def __init__(self, username, email, name, surname, is_operator):
        self.id = username
        self.email = email
        self.name = name
        self.surname = surname
        self.is_operator = is_operator
