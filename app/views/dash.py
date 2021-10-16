"""
Modulo contenente le route della dashboard amministratori.
Le route sono registrate nel Blueprint 'dash', con prefisso '/dashboard'.
"""

from datetime import datetime, date, timedelta

from flask import Blueprint, render_template, abort, request, current_app, flash, redirect, url_for
from sqlalchemy.sql import select, desc
from sqlalchemy.sql.expression import bindparam, func, case
from sqlalchemy.exc import IntegrityError, ProgrammingError
from werkzeug.security import generate_password_hash

from app.models.db import connect_as, Role, get_table_names, get_table_dictionary
from app.models.query import select_all
from app.models.db import (
    user_table, movie_table, projection_table,
    ticket_table, purchase_table, actor_movie_table,
    genre_table, payment_method_table, cast_member_table
)
from app.views.auth import operator_required


bp = Blueprint('dash', __name__, url_prefix='/dashboard')   # Blueprint per le route della dashboard amministratori


def is_recent(release_date):
    """Verifica se un film è recente, cioè pubblicato negli ultimi 9 mesi

    Args:
        release_date (Column - Datetime): la colonna rappresentante
            la data di rilascio del film

    Returns:
        bool: True se il film è stato rilasciato negli ultimi 9 mesi, False altrimenti
    """

    TIME_INTERVAL = 9 * 30              # 9 mesi
    return release_date + timedelta(days = TIME_INTERVAL) >= func.current_date()


def prepare_tuple(table_name, new_tuple):
    """Prepara la tupla per essere inserita nella tabella 'table_name', oppure per utilizzare i
    suoi campi come dati per aggiornare la tabella

    La preparazione consiste nel trasformare le date, la password e i boolean
    nella forma corretta per il database.

    Args:
        table_name (str): un nome di tabella valido
        new_tuple (dict): dizionario rappresentante una tupla,
            le chiavi devono avere gli stessi nomi degli
            attributi della tabella nel database

    Returns:
        dict: dizionario con i campi preparati per essere inseriti nel database
    """

    # trasforma dati provenienti da form che non sono nel formato corretto per il database
    if table_name == user_table.name:                   # tabella User
        if 'password' in new_tuple:
            new_tuple['password'] = generate_password_hash(new_tuple['password'])
        if 'birthdate' in new_tuple:
            new_tuple['birthdate'] = datetime.strptime(new_tuple['birthdate'], '%Y-%m-%d').date()
        new_tuple['isOperator'] = 'isOperator' in new_tuple

    elif table_name == movie_table.name:                # tabella Movie
        new_tuple['releaseDate'] = datetime.strptime(new_tuple['releaseDate'], '%Y-%m-%d').date()

    elif table_name == payment_method_table.name:       # tabella PaymentMethod
        new_tuple['expirationDate'] = datetime.strptime(new_tuple['expirationDate'], '%Y-%m-%d').date()
        new_tuple['isOperator'] = 'isActive' in new_tuple

    return new_tuple                                    # restituisce la nuova preparata per il database


def try_execute(query):
    """Esegue la funzione 'query' gestendo le eccezioni IntegrityError e ProgrammingError

    Args:
        query: funzione che esegue una query
            esempio: conn.execute(stmt)

    Returns:
        result_set (ResultProxy): le tuple risultanti
        error (str): messaggio di errore in caso di errore, None altrimenti
    """

    error = None
    result_set = None

    try:
        result_set = query()                # esegue la query e memorizza le tuple risultanti
    except IntegrityError as e:             # la query viola qualche vincolo di integrità
        error = "Constraint violation"
    except ProgrammingError as e:
        error = "Permission denied"         # l'utente ha un ruolo che non ha i permessi di eseguire la query

    if error:                               # in caso di errore, loggalo
        current_app.logger.info('Query failed: %s', error)

    return result_set, error                # restituisce tuple risultanti ed eventuale messaggio di errore


# lista di dizionari rappresentanti le fasce di età
AGE_GROUPS = [
    { 'name': '0-19', 'start': 0, 'end': 19 },
    { 'name': '20-29', 'start': 20, 'end': 29 },
    { 'name': '30-39', 'start': 30, 'end': 39 },
    { 'name': '40-49', 'start': 40, 'end': 49 },
    { 'name': '50-59', 'start': 50, 'end': 59 },
    { 'name': '60-69', 'start': 60, 'end': 69 },
    { 'name': '70-79', 'start': 70, 'end': 79 },
    { 'name': '80-99', 'start': 80, 'end': 99 }
]


def generate_additional_data(table_name):
    """Recupera dati utili per i form di inserimento/update

    In particolare permette di passare ai form nelle pagine html le
    informazioni di cui necessitano per mostare dei form user friendly.

    Args:
        table_name (str): il nome di una tabella del database

    Returns:
        additional_data (dict): dizionario contenete i dati addizionali
            per la tabella di input
    """

    additional_data = {}

    if table_name == actor_movie_table.name:                                # tabella ActorMovie
        additional_data['actors'] = select_all('CastMember')                # elenco cast members
        additional_data['movies'] = select_all('Movie')                     # elenco film

    elif table_name == movie_table.name:                                    # tabella Movie
        additional_data['directors'] = select_all('CastMember')             # elenco cast members
        additional_data['genres'] = select_all('Genre')                     # elenco generi
        additional_data['nations'] = select_all('Nation')                   # elenco nazioni

    elif table_name == projection_table.name:                               # tabella Projection
        additional_data['movies'] = select_all('Movie')                     # elenco film
        additional_data['rooms'] = select_all('Room')                       # elenco sale

    elif table_name == ticket_table.name:                                   # tabella Ticket
        additional_data['purchases'] = select_all('Purchase')               # elenco acquisti

    elif table_name == payment_method_table.name:                           # tabella PaymentMethod
        additional_data['users'] = select_all('User')                       # elenco utenti
        additional_data['payment_circuits'] = select_all('PaymentCircuit')  # elenco circuiti di pagamento

    elif table_name == purchase_table.name:                                 # tabella Purchase
        additional_data['users'] = select_all('User')                       # elenco utenti
        additional_data['projections'] = select_all('Projection')           # elenco proiezioni
        additional_data['payment_methods'] = select_all('PaymentMethod')    # elenco metodi di pagamento

    return additional_data


@bp.route('/')
@operator_required
def dashboard():
    """Route che renderizza la dashboard

    URL: /

    La route accetta 1 metodo, GET.
    GET: restituisce la pagina della dashboard

    Returns:
        str: html da renderizzare nel browser (dashboard)
    """

    return render_template('dash/index.html')                               # renderizza homepage dashboard


@bp.route('/tables')
@operator_required
def table_selection():
    """Route che permette di scegliere una tabella tra la lista di tabelle disponibili

    URL: /tables

    La route accetta 1 metodo, GET.
    GET: restituisce l'elenco delle tabelle disponibili

    Returns:
        str: html da renderizzare nel browser
    """

    # preleva dai parametri della richiesta GET l'identificativo della pagina
    # a cui redirezionare l'utente, una volta che ha scelto la tabella
    # valori validi: insert, read (default)
    next_ = request.args.get('next', 'read')

    table_names = get_table_names()                             # elenco dei nomi delle tabelle del db
    tables_to_hide = []                                         # elenco nomi tabelle da nascondere

    if next_ == 'read':                                         # pagina di read/update/delete
        tables_to_hide.extend([ payment_method_table.name ])    # nascondi PaymentMethod

    elif next_ == 'insert':                                     # pagina di insert
        tables_to_hide.extend([payment_method_table.name,       # nascondi PaymentMethod
                               ticket_table.name,               # nascondi Ticket
                               purchase_table.name,             # nascondi Purchase
                               user_table.name])                # nascondi User

    else:                                                       # pagina non riconosciuta
        abort(404)                                              # 404 NOT FOUND

    # rimuove tabelle da nascondere
    for table_name in tables_to_hide:                           # per ogni tabella tra quelle da nascondere
        table_names.remove(table_name)                          # rimuovi tabella

    # renderizza pagina di selezione tabelle, con le tabelle da mostrare
    return render_template("dash/table_selection.html", next=next_, table_names=table_names)


@bp.route('/tables/<table_name>')
@operator_required
def view_table(table_name):
    """Route che permette di visualizzare, aggiornare e cancellare tuple dalla tabella selezionata

    URL: /tables/<table_name>

    La route accetta 1 metodo, GET.
    GET: restituisce l'elenco delle tuple della tabella selezionata

    Args:
        table_name (str): nome della tabella del database da mostrare

    Returns:
        str: html da renderizzare nel browser
    """

    if table_name not in get_table_names():                 # se tabella non esiste
        abort(404)                                          # 404 NOT FOUND

    # sistema di paginazione
    size = request.args.get('size', 200, int)               # numero di risultati per pagina
    page = request.args.get('page', 1, int)                 # numero di pagina
    if size <= 0:                                           # dimensione pagina negativa o nulla
        size = 1                                            # limita inferiormente dimensione pagina a 1
    elif size > 500:                                        # se dimensione pagina troppo grande
        size = 500                                          # limita dimensione pagina a 500
    if page <= 0:                                           # numero di pagina negativo
        abort(404)                                          # 404 NOT FOUND
    offset = (page-1) * size                                # calcola offset per query

    error = None

    with connect_as(Role.OPERATOR) as conn:                     # connessione al database come operator
        table = get_table_dictionary()[table_name]              # ricava l'oggetto Table di sqlalchemy
        sel_stmt = select([table]).limit(size).offset(offset)   # seleziona porzione di database scelta
        result_set, error = try_execute(lambda: conn.execute(sel_stmt)) # esegue la query gestendo eventuali eccezioni

    if error:                           # in caso di errore
        return error                    # mostralo a schermo

    column_names = [ col.name for col in table.columns ]            # ricava i nomi delle colonne della tabella
    primary_key_names = [ col.name for col in table.primary_key ]   # nomi degli attributi che formano la PK

    # notare che c'è un unico template html per tutte le tabelle
    return render_template("dash/view_table.html",                  # renderizza tabella
                            table_name=table_name,                  # nome tabella
                            column_names=column_names,              # nomi attributi
                            primary_key_names=primary_key_names,    # nomi attributi PK
                            table_tuples=list(result_set),          # lista delle tuple
                            page=page,                              # pagina corrente
                            size=size)                              # dimensione pagina corrente


@bp.route('tables/<table_name>/insert', methods=('GET', 'POST'))
@operator_required
def insert_data(table_name):
    """Route che gestisce l'inserimento dei dati nelle tabelle

    URL: /tables/<table_name>/insert

    La route accetta 2 metodi, GET e POST.
    GET: restituisce il form di registrazione
    POST: preleva i dati dal form di registrazione, li valida
        e poi effettua l'inserimento del nuovo utente nel database

    Returns:
        str: html da renderizzare nel browser
    """

    if table_name not in get_table_names():                     # se tabella non esiste
        abort(404)                                              # 404 NOT FOUND

    if request.method == 'POST':                                # POST -> form con dati da inserire
        table = get_table_dictionary()[table_name]              # ricava l'oggetto Table di sqlalchemy
        column_names = [ col.name for col in table.columns ]    # ricava i nomi delle colonne della tabella

        # per ogni campo del form con nome uguale al nome di un attributo della tabella selezionata
        # inserisce una entry nel dizionario (nome_attributo, valore_attributo)
        # di fatto genera una tupla con gli attributi corretti per il database
        new_tuple = { key: value for key, value in request.form.items() if key in column_names }
        # corregge i campi che hanno un formato diverso da quello che il database si aspetta
        new_tuple = prepare_tuple(table_name, new_tuple)

        error = None

        with connect_as(Role.OPERATOR) as conn:                 # connessione al database come operator
            ins_stmt = table.insert()                           # crea la query di inserimento
            # esegue la query gestendo eventuali eccezioni
            _, error = try_execute(lambda: conn.execute(ins_stmt, [new_tuple]))

        flash(error or 'Success', 'danger' if error else 'success')
        return error or redirect(url_for('dash.insert_data', table_name=table_name))

    else:                                                               # GET -> renderizza form
        # genera dati addizionali utili per i form e renderizza il form corretto in base al nome della tabella
        additional_data = generate_additional_data(table_name)
        return render_template(f'dash/insert_update_forms/insert_{table_name}.html',
                               table_name=table_name,                   # nome della tabella
                               additional_data=additional_data)         # dati addizionali


@bp.route('tables/<table_name>/update', methods=('GET', 'POST'))
@operator_required
def update_data(table_name):
    """Route che gestisce la fase di update

    URL: /tables/<table_name>/update

    La route accetta 2 metodi, GET e POST.
    GET: restituisce il form per l'update
    POST: preleva i dati dal form di update, e poi effettua
        l'update dei dati nel database

    Returns:
        str: html da renderizzare nel browser
    """

    if table_name not in get_table_names():                         # se tabella non esiste
        abort(404)                                                  # 404 NOT FOUND

    table = get_table_dictionary()[table_name]                      # ricava l'oggetto Table di sqlalchemy
    primary_key_names = [ col.name for col in table.primary_key ]   # nomi degli attributi che formano la PK

    if request.method == 'POST':                                    # POST -> form con dati da aggiornare

        column_names = [ col.name for col in table.columns ]        # ricava i nomi delle colonne della tabella

        # per ogni campo del form con nome uguale al nome di un attributo della tabella selezionata
        # inserisce una entry nel dizionario (nome_attributo, valore_attributo)
        # di fatto genera una tupla con gli attributi corretti per il database
        new_tuple = { key: value for key, value in request.form.items() if key in column_names }
        # corregge i campi che hanno un formato diverso da quello che il database si aspetta
        new_tuple = prepare_tuple(table_name, new_tuple)

        # crea la statement di update (un WHERE per ogni colonna della PK)
        upd_stmt = table.update()
        for pk_name in primary_key_names:                                               # per ogni colonna della PK
            upd_stmt = upd_stmt.where(table.c[pk_name] == bindparam(pk_name + '_old'))  # imposta condizione su colonna
        upd_stmt = upd_stmt.values(**new_tuple)                             # passa la tupla con i dati da aggiornare

        # crea un dizionario da passare come input alla query per risolvere i parametri (bindparam)
        # da notare che utilizza la primary key precedente all'update (pk_name_old),
        # che deve quindi essere passata dal form
        param_dict = { pk_name + '_old': request.form[pk_name + '_old'] for pk_name in primary_key_names }

        error = None

        with connect_as(Role.OPERATOR) as conn:                     # connessione al database come operator
            _, error = try_execute(lambda: conn.execute(upd_stmt, **param_dict))

        return error or redirect(url_for('dash.view_table', table_name=table_name))

    else:                                                           # GET -> renderizza form
        # carica tupla da aggiornare dal database
        # genera SELECT statement
        sel_stmt = table.select()
        for pk_name in primary_key_names:                                       # per ogni colonna della PK
            sel_stmt = sel_stmt.where(table.c[pk_name] == bindparam(pk_name))   # imposta condizione su colonna

        # crea un dizionario da passare come input alla query per risolvere i parametri (bindparam)
        param_dict = { pk_name: request.args[pk_name] for pk_name in primary_key_names }

        error = None

        with connect_as(Role.OPERATOR) as conn:                     # connessione al database come operator
            # esegue la query gestendo eventuali eccezioni
            result_set, error = try_execute(lambda: conn.execute(sel_stmt, **param_dict))
            if error:                                                   # se si è verificato un errore
                return error                                            # mostralo a schermo
            res = result_set.first()
            if res:
                res = dict(res)
            else:
                abort(404)

        # genera dati addizionali utili per i form e renderizza il form corretto in base al nome della tabella
        additional_data = generate_additional_data(table_name)
        return render_template(f"dash/insert_update_forms/insert_{table_name}.html",
                               table_name=table_name,                   # nome tabella
                               primary_key_names=primary_key_names,     # nomi attributi della PK
                               additional_data=additional_data,         # dati addizionali
                               tuple=res)          # tupla


@bp.route('/tables/<table_name>/delete', methods=('GET', 'POST'))
@operator_required
def delete_row(table_name):
    """Route che gestisce la fase di cancellazione di una tupla

    URL: /tables/<table_name>/delete

    La route accetta 2 metodi, GET e POST.
    GET: mostra una pagina di conferma di eliminazione
    POST: preleva la PK, della tupla da eliminare, dal form,
        poi invia delete al database e redireziona alla pagina
        che mostra la tabella (tables/<table_name>)

    Returns:
        str: html da renderizzare nel browser
    """
    if table_name not in get_table_names():                         # se tabella non esiste
        abort(404)                                                  # 404 NOT FOUND

    table = get_table_dictionary()[table_name]                      # ricava l'oggetto Table di sqlalchemy
    primary_key_names = [ col.name for col in table.primary_key ]   # nomi degli attributi che formano la PK

    # genera la statement da passare al database (GET: select; POST: delete)
    stmt = table.select() if request.method == 'GET' else table.delete()
    for pk_name in primary_key_names:                                       # per ogni colonna della PK
        stmt = stmt.where(table.c[pk_name] == bindparam(pk_name))           # imposta condizione su colonna

    # crea un dizionario da passare come input alla query per risolvere i parametri (bindparam)
    request_data = request.args if request.method == 'GET' else request.form    # nomi degli attributi che formano la PK
    param_dict = { pk_name: request_data[pk_name] for pk_name in primary_key_names }

    error = None

    with connect_as(Role.OPERATOR) as conn:                                         # connessione al database come client
        result_set, error = try_execute(lambda: conn.execute(stmt, **param_dict))   # esegue la query gestendo eventuali eccezioni

    if error:                                                               # in caso di errore
        return error                                                        # mostralo a schermo

    if request.method == 'GET':                                             # GET -> pagina di conferma
        return render_template('dash/delete.html',                          # renderizza pagina di conferma
                               table_name=table_name,                       # nome tabella
                               primary_key_names=primary_key_names,         # nomi attributi PK
                               tuple=result_set.first())                    # tupla da rimuovere

    else:                                                                   # POST -> effettua cancellazione
        #flash('Row deleted', 'success')                                    # flasha messaggio di successo
        return redirect(url_for('dash.view_table', table_name=table_name))  # redieziona a pagina di visualizzazione tabella


@bp.route('/statistics')
@operator_required
def statistics():
    """Route che calcola e mostra alcune statistiche

    URL: /statistics

    La route accetta 1 metodo, GET.
    GET: mostra una pagina di con una serie di statistiche

    Returns:
        str: html da renderizzare nel browser (pagina di statistiche)
    """


    with connect_as(Role.WEBAPP) as conn:                   # connessione al database come webapp

        # mostra i generi più comuni tra i film proiettati dal cinema in ordine non crescente (decrescente)
        # conta il numero di film per ogni genrere
        select_common_movie_genre = (
            select([
                movie_table.c.genre,
                func.count().label('genre_count')
            ]).group_by(
                movie_table.c.genre
            ).order_by(
                desc('genre_count')
            )
        )
        common_movie_genre = conn.execute(select_common_movie_genre)

        # mostra i generi di film più popolari tra i clienti del cinema in ordine non crescente (decrescente)
        # conta numero di biglietti venduti per genere
        select_movie_genre_popularity = (
            select_common_movie_genre.\
            where(
                (movie_table.c.id == projection_table.c.movie)
                & (projection_table.c.id == purchase_table.c.projection)
                & (purchase_table.c.id == ticket_table.c.purchase)
            )
        )
        movie_genre_popularity = conn.execute(select_movie_genre_popularity)

        # mostra i generi di film del cinema più redditizi in ordine non crescente (decrescente)
        # calcola entrate per ogni genere
        select_profitable_movie_genre = (
            select([
                movie_table.c.genre,
                func.sum(purchase_table.c.total).label('genre_profit')
            ]).where(
                (movie_table.c.id == projection_table.c.movie)
                & (projection_table.c.id == purchase_table.c.projection)
            ).group_by(
                movie_table.c.genre
            ).order_by(
                desc('genre_profit')
            )
        )
        movie_genre_profits = conn.execute(select_profitable_movie_genre)

        # mostra i generi di film più popolari tra i clienti del cinema in base all'età in ordine dagli utenti più giovani ai più vecchi
        # mostra per ogni genere, quali sono le fascie d'età che lo seguono di più
        current_year = datetime.now().year
        genres = conn.execute(select([genre_table]).order_by(genre_table.c.name))

        select_genre_popularity_by_age = (
            select([
                movie_table.c.genre,
                case(                       # creazione dinamica dei casi per la clausola case
                    [
                        (
                            (current_year - func.extract('year', user_table.c.birthdate) >= age_group['start'])
                            & (current_year - func.extract('year', user_table.c.birthdate) <= age_group['end']),
                            age_group['name']
                        )
                        for age_group in AGE_GROUPS
                    ],
                    else_='100+'
                ).label('age_group'),
                func.count().label('ticket_count')
            ]).where(
                (movie_table.c.id == projection_table.c.movie)
                & (projection_table.c.id == purchase_table.c.projection)
                & (purchase_table.c.id == ticket_table.c.purchase)
                & (purchase_table.c.paymentMethod == payment_method_table.c.id)
                & (payment_method_table.c.user == user_table.c.username)
            ).group_by(
                'age_group',
                movie_table.c.genre
            ).order_by(
                desc('ticket_count')
            )
        )
        result_set = conn.execute(select_genre_popularity_by_age)
        result_list = result_set.fetchall()

        genre_popularity_by_age = { genre['name']: [] for genre in genres }
        age_popularity_by_genre = { age_group['name']: [] for age_group in AGE_GROUPS }

        for row in result_list:
            genre_popularity_by_age[row['genre']].append({
                'age_group': row['age_group'],
                'ticket_count': row['ticket_count']
            })

            age_popularity_by_genre[row['age_group']].append({
                'genre': row['genre'],
                'ticket_count': row['ticket_count']
            })

        # limita i risultati a 3 per ogni categoria
        LIMIT = 3
        for genre in genre_popularity_by_age:
            genre_popularity_by_age[genre] = genre_popularity_by_age[genre][:LIMIT]
        for age_group in age_popularity_by_genre:
            age_popularity_by_genre[age_group] = age_popularity_by_genre[age_group][:LIMIT]


        # mostra i generi più comuni nel trend degli ultimi 9 mesi tra i film proiettati dal cinema in ordine non crescente (decrescente)
        select_common_movie_genre_trend = (
            select_common_movie_genre.\
            where(is_recent(movie_table.c.releaseDate))
        )
        common_movie_genre_trend = conn.execute(select_common_movie_genre_trend)

        # mostra i generi di film più popolari degli ultimi 9 mesi tra i clienti del cinema in ordine non crescente (decrescente)
        select_movie_genre_popularity_trend = (
            select_movie_genre_popularity.\
            where(is_recent(movie_table.c.releaseDate))
        )
        movie_genre_popularity_trend = conn.execute(select_movie_genre_popularity_trend)

        # mostra i generi di film del cinema più redditizi negli ultimi 9 mesi in ordine non crescente (decrescente)
        select_profitable_movie_genre_trend = (
            select_profitable_movie_genre.\
            where(is_recent(movie_table.c.releaseDate))
        )
        movie_genre_profits_trend = conn.execute(select_profitable_movie_genre_trend)

        # mostra gli attori più popolari tra i clienti del cinema in ordine non crescente (decrescente)
        # attori che hanno venduto più biglietti
        select_popular_actors = (
            select([
                cast_member_table.c.name,
                cast_member_table.c.surname,
                func.count().label('ticket_count')
            ]).where(
                (cast_member_table.c.id == actor_movie_table.c.actor)
                & (actor_movie_table.c.movie == movie_table.c.id)
                & (movie_table.c.id == projection_table.c.movie)
                & (projection_table.c.id == purchase_table.c.projection)
                & (purchase_table.c.id == ticket_table.c.purchase)
            ).group_by(
                cast_member_table.c.id
            ).order_by(
                desc('ticket_count')
            ).limit(25)
        )
        popular_actors = conn.execute(select_popular_actors)

        # mostra i registi più popolari tra i clienti del cinema in ordine non crescente (decrescente)
        # registi che hanno venduto più biglietti
        select_popular_directors = (
            select([
                cast_member_table.c.name,
                cast_member_table.c.surname,
                func.count().label('ticket_count')
            ]).where(
                (cast_member_table.c.id == movie_table.c.director)
                & (movie_table.c.id == projection_table.c.movie)
                & (projection_table.c.id == purchase_table.c.projection)
                & (purchase_table.c.id == ticket_table.c.purchase)
            ).group_by(
                cast_member_table.c.id
            ).order_by(
                desc('ticket_count')
            ).limit(25)
        )
        popular_directors = conn.execute(select_popular_directors)

    # renderizza statistiche calcolate
    return render_template('dash/statistics.html',
                           common_movie_genre=common_movie_genre,
                           movie_genre_popularity=movie_genre_popularity,
                           movie_genre_profits=movie_genre_profits,
                           common_movie_genre_trend=common_movie_genre_trend,
                           movie_genre_popularity_trend=movie_genre_popularity_trend,
                           movie_genre_profits_trend=movie_genre_profits_trend,
                           genre_popularity_by_age=genre_popularity_by_age,
                           age_popularity_by_genre=age_popularity_by_genre,
                           popular_actors=popular_actors,
                           popular_directors=popular_directors)
