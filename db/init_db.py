#!/usr/bin/env python3

"""Inizializza il database caricando opportuni dati nel database"""

import os
import random
import urllib.parse
from datetime import datetime, date, timedelta

from sqlalchemy import create_engine
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import func
from werkzeug.security import generate_password_hash

from app.models.db import init_db, get_db
from app.models.db import (
    user_table, genre_table, cast_member_table,
    movie_table, room_table, payment_method_table,
    projection_table, actor_movie_table, nation_table,
    ticket_table, purchase_table, payment_circuit_table
)


# https://randomuser.me/api/?results=250&inc=gender,name,nat,email,login,registered,dob

# # load environment variables
# DIALECT = os.getenv("DIALECT")
# DB_ADMIN_USER = os.getenv("DB_ADMIN_USER")
# DB_ADMIN_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_ADMIN_PASSWORD"))
# DB_APP_USER = os.getenv("DB_APP_USER")
# DB_APP_PASSWORD = urllib.parse.quote_plus(os.getenv("DB_APP_PASSWORD"))
# DB_HOST = os.getenv("DB_HOST")
# DB_PORT = os.getenv("DB_PORT")
# DB_NAME = os.getenv("DB_NAME")

# # sqlalchemy compliant database url
# DB_STRING = f"{DIALECT}://{DB_ADMIN_USER}:{DB_ADMIN_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


# db = create_engine(DB_STRING, pool_pre_ping=True)


import json


HASH_PASSWORD = False       # False in fase di test per accelerare la fase di start-up
random.seed(1)


def get_fake_users():
    """Restituisce una lista di utenti fake"""

    with open('db/fake-data/users.json') as f:
        data = json.load(f)

        users = []
        for row in data['results']:
            user = {
                'username': row['login']['username'],
                'email': row['email'],
                'password': generate_password_hash(row['login']['password']) if HASH_PASSWORD else row['login']['password'],
                'name': row['name']['first'],
                'surname': row['name']['last'],
                'birthdate': datetime.strptime(row['dob']['date'], '%Y-%m-%dT%H:%M:%S.%fZ').date(),
                'registrationDate': datetime.strptime(row['registered']['date'], '%Y-%m-%dT%H:%M:%S.%fZ').date(),
                'isOperator': False
            }
            users.append(user)

        users.extend([
            {
                'username': 'test',
                'email': 'test@gmail.com',
                'password': generate_password_hash('test'),
                'name': 'TestName',
                'surname': 'TestSurname',
                'birthdate': date(2000, 2, 18),
                'registrationDate': date(2020, 6, 6),
                'isOperator': True
            },
            {
                'username': 'prova',
                'email': 'prova@gmail.com',
                'password': generate_password_hash('prova'),
                'name': 'ProvaName',
                'surname': 'ProvaSurname',
                'birthdate': date(1995, 7, 21),
                'registrationDate': date(2020, 6, 10),
                'isOperator': False
            },
            {
                'username': 'operatore',
                'email': 'operatore@gmail.com',
                'password': generate_password_hash('operatore'),
                'name': 'OperatoreName',
                'surname': 'OperatoreSurname',
                'birthdate': date(1980, 9, 10),
                'registrationDate': date(2019, 12, 12),
                'isOperator': True
            }
        ])

        return users


def get_genres():
    """Restituisce la lista dei generi esistenti"""

    genres = [
        {'name': 'Comedy'},
        {'name': 'Documentary'},
        {'name': 'Drama'},
        {'name': 'Action'},
        {'name': 'Adventure'},
        {'name': 'Horror'},
        {'name': 'Mystery'},
        {'name': 'Crime'},
        {'name': 'Sci-Fi'},
        {'name': 'Western'},
        {'name': 'Biography'},
        {'name': 'Thriller'},
        {'name': 'Fantasy'},
        {'name': 'Family'},
        {'name': 'Animation'}
    ]

    return genres


def get_nations():
    """Restituisce la lista dei generi esistenti"""

    nations = [
        {'name': 'Italy'},
        {'name': 'USA'},
        {'name': 'France'},
        {'name': 'UK'},
        {'name': 'Japan'},
        {'name': 'Indonesia'},
        {'name': 'Canada'},
        {'name': 'Mexico'},
        {'name': 'Germany'},
        {'name': 'Australia'},
        {'name': 'New Zealand'},
        {'name': 'Ireland'},
        {'name': 'Mozambique'}
    ]

    return nations


def get_actors():
    """Restituisce una lista di attori"""

    with open('db/fake-data/actors.json') as f:
        data = json.load(f)

        actors = []
        for row in data:
            actor = {
                'name': row['name'],
                'surname': row['surname']
            }
            actors.append(actor)

        return actors


def get_rooms():
    random.seed(1)

    rooms = []

    min_rows = 10
    max_rows = 35
    min_cols = 10
    max_cols = 20
    min_size = 100
    max_size = 200


    letters = [ 'A', 'B', 'C', 'D', 'E']
    numbers = [ '1', '2', '3', '4', '5']

    for letter in letters:
        for number in numbers:
            room = {
                'name': letter + number,
                'numberOfRows': random.randint(min_rows, max_rows),
                'numberOfColumns': random.randint(min_cols, max_cols),
                'screenSize': random.randint(min_size, max_size)
            }
            rooms.append(room)

    return rooms


def get_directors():
    """Restituisce una lista di registi"""

    with open('db/fake-data/directors.json') as f:
        data = json.load(f)

        directors = []
        for row in data:
            director = {
                'name': row['name'],
                'surname': row['surname']
            }
            directors.append(director)

        return directors


def get_cast_members():
    return get_actors() + get_directors()


def get_fake_projections():
    random.seed(1)

    projections = []
    rooms = get_rooms()

    db = get_db()
    with db.connect() as conn:
        sel_stmt = select([
            func.count().label('numberOfMovies')
        ]).select_from(movie_table)
        results = conn.execute(sel_stmt)
        number_of_movies = results.first()['numberOfMovies']

    # random projection near current date
    for _ in range(1000):
        projection = {
            'movie': random.randint(1, number_of_movies),
            'room': random.choice(rooms)['name'],
            'datetime': datetime.now() + timedelta(days=random.randint(-7, 7), hours=random.randint(-23, 23)),
            'price': random.randint(3, 10)
        }
        projections.append(projection)

    # random projection in the past
    for _ in range(1000):
        projection = {
            'movie': random.randint(1, number_of_movies),
            'room': random.choice(rooms)['name'],
            'datetime': datetime.now() - timedelta(days=random.randint(15, 365), hours=random.randint(0, 23)),
            'price': random.randint(3, 10)
        }
        projections.append(projection)

    return projections


def get_payment_circuits():
    """Restituisce la lista dei circuiti di pagamento esistenti"""

    payment_circuits = [
        {'name': 'Mastercard'},
        {'name': 'Visa'},
        {'name': 'American Express'},
        {'name': 'Diners Club'}
    ]

    return payment_circuits


def get_fake_payment_methods():
    random.seed(1)

    payment_methods = []

    users = get_fake_users()
    payment_circuits = get_payment_circuits()

    for user in users:
        number_of_payment_methods = random.randint(0, 3)

        for _ in range(number_of_payment_methods):
            payment_method = {
                'ownerName': user['name'] + ' ' + user['surname'],
                'user': user['username'],
                'cardNumber': ''.join(str(random.randint(0, 9)) for _ in range(16)),
                'expirationDate': date(random.randint(2019, 2030), random.randint(1, 12), random.randint(1, 28)),
                'paymentCircuit': random.choice(payment_circuits)['name'],
                'isActive': True
            }
            payment_methods.append(payment_method)

    return payment_methods


def get_fake_purchases():
    random.seed(1)

    purchases = []
    payment_methods = get_fake_payment_methods()
    projection_count = len(get_fake_projections())
    payment_count = len(payment_methods)

    for _ in range(10000):
        purchase = {
            'projection': random.randint(1, projection_count),
            'total': random.randint(1, 100),                    # per ora non è legato al vero valore
            'purchaseDatetime': datetime.now() - timedelta(days=random.randint(0, 500), hours=random.randint(0, 23)),
            'paymentMethod': random.randint(1, payment_count)
        }
        purchases.append(purchase)

    # ogni proiezione ha almeno un acquisto
    for projection_id in range(1, projection_count+1):
        purchase = {
            'projection': projection_id,
            'total': random.randint(1, 100),                    # per ora non è legato al vero valore
            'purchaseDatetime': datetime.now() - timedelta(days=random.randint(0, 500), hours=random.randint(0, 23)),
            'paymentMethod': random.randint(1, payment_count)
        }
        purchases.append(purchase)

    return purchases


def get_movies():
    with open('db/fake-data/movies.json') as f:
        data = json.load(f)
        return data


def get_fake_tickets():
    random.seed(1)

    tickets = []
    purchase_count = len(get_fake_purchases())

    for purchase_id in range(1, purchase_count+1):
        ticket_count = random.randint(1, 10)

        for _ in range(ticket_count):
            ticket = {
                'row': random.randint(1, 10),
                'column': random.randint(1, 10),
                'purchase': purchase_id,
            }

            tickets.append(ticket)

    return tickets


def insert_movies_actors_director(conn):
    random.seed(1)

    movies = get_movies()

    for movie in movies:

        # aggiunge gli attori che non sono contenuti nel database
        for actor in movie['actors']:
            trans = conn.begin()
            try:
                sel_stmt = select([
                    cast_member_table
                ]).where(
                    (cast_member_table.c.name == actor['name'])
                    & (cast_member_table.c.surname == actor['surname'])
                )
                results = conn.execute(sel_stmt)
                row = results.first()
                if not row:
                    ins_stmt = cast_member_table.insert()
                    conn.execute(ins_stmt, actor)
                trans.commit()          # commit
            except:
                trans.rollback()        # rollback
                raise

        # aggiunge il regista se non è contenuto nel database
        director = movie['director']
        trans = conn.begin()
        try:
            sel_stmt = select([
                cast_member_table
            ]).where(
                (cast_member_table.c.name == director['name'])
                & (cast_member_table.c.surname == director['surname'])
            )
            results = conn.execute(sel_stmt)
            row = results.first()
            if not row:
                ins_stmt = cast_member_table.insert()
                conn.execute(ins_stmt, director)
            trans.commit()          # commit
        except:
            trans.rollback()        # rollback
            raise

        # aggiunge il film
        trans = conn.begin()
        try:
            # trova l'id del regista
            sel_stmt = select([
                cast_member_table.c.id
            ]).where(
                (cast_member_table.c.name == director['name'])
                & (cast_member_table.c.surname == director['surname'])
            )
            results = conn.execute(sel_stmt)
            row = results.first()
            director_id = row['id']

            # trova gli id degli attori che recitano nel film
            actor_ids = []
            for actor in movie['actors']:
                sel_stmt = select([
                    cast_member_table.c.id
                ]).where(
                    (cast_member_table.c.name == actor['name'])
                    & (cast_member_table.c.surname == actor['surname'])
                )
                results = conn.execute(sel_stmt)
                actor_ids.append(results.first()['id'])

            # inserisce il film
            curr_date = datetime.now()
            ins_stmt = movie_table.insert()
            conn.execute(ins_stmt, [
                {
                    'title': movie['title'],
                    'director': director_id,
                    'plot': movie['plot'],
                    'duration': int(movie['duration']),
                    'genre': movie['genre'],
                    'nation': movie['nation'],
                    'releaseDate': date(
                        int(movie['year']),
                        random.randint(1, curr_date.month if curr_date.year == int(movie['year']) else 12),
                        random.randint(1, curr_date.day if curr_date.year == int(movie['year']) else 28)
                    ),
                    'poster': movie['poster']
                }
            ])

            # inserisce attori al film
            for actor_id in actor_ids:
                sel_stmt = select([
                    movie_table.c.id
                ]).where(
                    (movie_table.c.title == movie['title'])
                    & (movie_table.c.director == director_id)
                )
                results = conn.execute(sel_stmt)
                movie_id = results.first()['id']

                ins_stmt = actor_movie_table.insert()
                conn.execute(ins_stmt, [
                    {
                        'movie': movie_id,
                        'actor': actor_id
                    }
                ])

            trans.commit()          # commit
        except:
            trans.rollback()        # rollback
            raise


def load_fake_data(conn):

    # insert users
    ins = user_table.insert()
    conn.execute(ins, get_fake_users())

    # insert genres
    ins = genre_table.insert()
    conn.execute(ins, get_genres())

    # insert genres
    ins = nation_table.insert()
    conn.execute(ins, get_nations())

    # insert cast members
    ins = cast_member_table.insert()
    conn.execute(ins, get_cast_members())

    # insert movies with corresponding actors and director
    insert_movies_actors_director(conn)


    # insert rooms
    ins = room_table.insert()
    conn.execute(ins, get_rooms())

    # insert projections
    ins = projection_table.insert()
    conn.execute(ins, get_fake_projections())

    # insert payment circuits
    ins = payment_circuit_table.insert()
    conn.execute(ins, get_payment_circuits())

    # insert payment methods
    ins = payment_method_table.insert()
    conn.execute(ins, get_fake_payment_methods())
    random.seed(1)
    conn.execute(ins, [{
        'ownerName': 'TestName TestSurname',
        'user': 'test',
        'cardNumber': ''.join(str(random.randint(0, 9)) for _ in range(16)),
        'expirationDate': date(random.randint(2019, 2030), random.randint(1, 12), random.randint(1, 28)),
        'paymentCircuit': 'Visa',
        'isActive': True
    }])

    # insert purchases
    ins = purchase_table.insert()
    conn.execute(ins, get_fake_purchases())

    # insert tickets
    ins = ticket_table.insert()
    conn.execute(ins, get_fake_tickets())


# def load_real_data(conn):

#     # insert genres
#     ins = movie_table.insert()
#     conn.execute(ins, get_genres())

#     # insert cast members
#     ins = cast_member_table.insert()
#     conn.execute(ins, get_cast_members)



# legge le query per creare il database
with open('db/sql/schema.sql', 'r') as f:
    queries = f.read()

# legge le query per creare i ruoli della web app
with open('db/sql/privilegies.sql', 'r') as f:
    conf = f.read()


db = get_db()
with db.connect() as conn:
    conn.execute(queries)                   # crea tabelle database
    conn.execute(conf)                      # crea ruoli database
    load_fake_data(conn)                    # carica dati fake
