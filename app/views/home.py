"""
Modulo contenente le route della home (ovvero quelle principali).
Le route sono registrate nel Blueprint 'home' (e sono senza prefisso url).
"""

import time
import random
from datetime import datetime

from flask import (
    Blueprint, render_template, request, abort, session, current_app, redirect, url_for, flash
)
from flask_login import login_required, current_user
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import bindparam

from app.models.db import connect_as, Role
from app.models.db import (
    movie_table, projection_table, room_table,
    ticket_table, purchase_table, cast_member_table,
    actor_movie_table, payment_circuit_table,
    payment_method_table, genre_table
)


bp = Blueprint('home', __name__)        # Blueprint per le route della homepage


@bp.route('/')
def home():
    """Route che renderizza la homepage

    URL: /

    La route accetta 1 metodo, GET.
    GET: restituisce la homepage

    Returns:
        str: html da renderizzare nel browser (homepage)
    """

    return render_template('home/index.html')


@bp.route('/movies')
def movies():
    """Route che mostra elenco film disponibili (in programmazione)

    La pagina permette anche di filtrare i film per genere e titolo.

    URL: /movies

    La route accetta 1 metodo, GET.
    GET: restituisce l'elenco dei film disponibili

    Returns:
        str: html da renderizzare nel browser
    """

    # preleva i valori dei parametri GET (necessari per implementare filtro)
    input_genres = request.args.getlist('genre', None)      # generi selezionati
    input_search = request.args.get('search', None, str)    # testo nella barra di ricerca
    search_sql = ''

    # carica film dal database
    with connect_as(Role.CLIENT) as conn:                   # connessione al database come client

        # seleziona i generi disponibili
        sel_stmt = select([
            genre_table.c.name
        ])
        results = conn.execute(sel_stmt)                    # effettua query
        all_genres = results.fetchall()                     # salva lista generi

        # seleziona film con proiezioni future programmate (con eventuale filtro per genere)
        sel_stmt = select([
            movie_table.c.id,
            movie_table.c.title,
            movie_table.c.plot,
            movie_table.c.genre,
            movie_table.c.poster
        ]).where(
            (projection_table.c.movie == movie_table.c.id)      # condizione di join
            & (projection_table.c.datetime >= datetime.now())   # solo film in programmazione nel futuro
        ).distinct()                                            # rimuove duplicati

        if len(input_genres) > 0:                               # se ci sono generi selezionati
            sel_stmt = sel_stmt.where(                          # film dei generi selezionati
                movie_table.c.genre.in_(bindparam('genres', expanding=True))    # sql IN
            )

        if input_search:                                        # se c'è del testo nella barra di ricerca
            search_sql = f'%{input_search}%'                    # va bene che la query string sia in mezzo
            sel_stmt = sel_stmt.where(                          # film con titolo che matcha la query string
                (movie_table.c.title.ilike(bindparam('search_title')))
            )

        # esegui query e prendi i risultati
        results = conn.execute(sel_stmt, genres=input_genres, search_title=search_sql)
        movies = results.fetchall()

    return render_template('home/movies.html',                  # renderizza lista film
                           movies=movies,                       # lista film
                           genres=all_genres,                   # lista generi
                           selected_genres=input_genres,        # genere selezionato
                           search_field=input_search)           # stringa di ricerca


@bp.route('/movies/<int:movie_id>')
def movie(movie_id):
    """Route che mostra dettagli sul film selezionato (movie_id)

    URL: /movies/<int:movie_id>

    La route accetta 1 metodo, GET.
    GET: restituisce l'elenco dei film disponibili

    Args:
        movie_id (int): id del film

    Returns:
        str: html da renderizzare nel browser
    """

    # carica film, attori, regista e proiezioni dal database
    with connect_as(Role.CLIENT) as conn:                           # connessione al database come client
        # seleziona film (+ info sul regista) con id uguale a movie_id
        sel_stmt = select([
            movie_table,
            cast_member_table.c.name.label('directorName'),
            cast_member_table.c.surname.label('directorSurname')
        ]).where(
            (movie_table.c.director == cast_member_table.c.id)      # condizione di join
            & (movie_table.c.id == bindparam('movie_id'))           # stesso id
        )
        result_set = conn.execute(sel_stmt, movie_id=movie_id)      # esegui query
        movie = result_set.first()                                  # al più uno (un solo regista e movie_id è PK)

        # seleziona attori del film
        sel_stmt = select([
            cast_member_table
        ]).where(
            (cast_member_table.c.id == actor_movie_table.c.actor)   # condizione di join
            & (actor_movie_table.c.movie == bindparam('movie_id'))  # stesso id
        )
        result_set = conn.execute(sel_stmt, movie_id=movie_id)      # esegui query
        actors = result_set.fetchall()

        # seleziona proiezioni programmate per il film
        sel_stmt = select([
            projection_table.c.id,
            projection_table.c.room,
            projection_table.c.datetime,
            projection_table.c.price
        ]).where(
            (projection_table.c.movie == bindparam('movie_id'))     # proiezioni del film richiesto
            & (projection_table.c.datetime >= datetime.now())       # solo proiezioni future
        ).order_by(
            projection_table.c.datetime                             # ordinate per data
        )
        result_set = conn.execute(sel_stmt, movie_id=movie_id)      # esegui query
        projections = result_set.fetchall()

    # renderizza pagina con dettagli film
    return render_template('home/movie.html', movie=movie, actors=actors, projections=projections)


@bp.route('/seats/<int:proj_id>')
@login_required
def seats(proj_id):
    """Route che mostra una pagina per la scelta dei posti

    URL: /seats/<int:proj_id>

    La route accetta 1 metodo, GET.
    GET: restituisce un form per la scelta dei posti

    Args:
        proj_id (int): id della proiezione

    Returns:
        str: html da renderizzare nel browser (selezionatore posti)
    """

    error = None

    with connect_as(Role.CLIENT) as conn:                           # connessione al database come client
        # leggi quanti posti ha la sala
        sel_stmt = select([
            room_table.c.numberOfRows,
            room_table.c.numberOfColumns
        ]).where(
            (room_table.c.name == projection_table.c.room)          # condizione di join
            & (projection_table.c.id == bindparam('proj_id'))       # projection id uguale a quello selezionato
            & (projection_table.c.datetime >= datetime.now())       # solo proiezioni future
        )
        results = conn.execute(sel_stmt, proj_id=proj_id)
        row = results.first()
        if not row:
            abort(404)

        row_count = row['numberOfRows']                             # numero di righe sala
        col_count = row['numberOfColumns']                          # numero di colonne sala

        seats = [[True]*col_count for _ in range(row_count)]        # matrice dei posti (sale rettangolari)

        # trova posti occupati
        sel_stmt = select([
            ticket_table.c.row,
            ticket_table.c.column
        ]).where(
            (purchase_table.c.projection == bindparam('proj_id'))
            & (ticket_table.c.purchase == purchase_table.c.id)
        )
        results = conn.execute(sel_stmt, proj_id=proj_id)
        for result in results:              # per ogni biglietto venduto
            # riga e colonna occupata (-1 perchè posti sono 1-based, mentre seats list e 0-based)
            row = result['row'] - 1
            col = result['column'] - 1
            seats[row][col] = False         # aggiorna matrice dei posti (segnala posto occupato)

    # renderizza selezionatore posti
    return render_template('home/seats.html', seats=seats, proj_id=proj_id)


@bp.route('/checkout', methods=('POST',))
@login_required
def checkout():
    """Route che mostra il riepilogo dell'acquisto e permette di scegliere metodo di pagamento

    URL: /checkout

    La route accetta 1 metodo, POST.
    POST: mostra il riepilogo dell'acquisto e form selezione
        metodo di pagamento

    Returns:
        str: html da renderizzare nel browser
    """

    error = None

    # analizza contenuto form per conoscere i posti selezionati
    seats = []
    for seat in request.form:                               # itera su tutti i posti selezionati
        if (',' in seat) and (request.form[seat] == 'on'):  # verifica che siano davvero selezionati
            # calcola riga e colonna in base all'id del posto
            row_col = seat.split(',')                       # divide id posto (row,col)
            row = int(row_col[0])                           # l'indice di riga è il primo
            column = int(row_col[1])                        # l'indice di colonna è il secondo
            seats.append({                                  # aggiunge posto alla lista dei posti
                'row': row,
                'column': column
            })

    if len(seats) == 0:
        error = 'No ticket selected'

    # recupera il titolo del film, il prezzo del biglietto e l'orario
    with connect_as(Role.CLIENT) as conn:                           # connessione al database come client
        sel_stmt = select([
            movie_table.c.title,                                    # seleziona il titolo
            projection_table.c.price,                               # seleziona il prezzo
            projection_table.c.datetime                             # seleziona l'orario
        ]).where(
            (projection_table.c.movie == movie_table.c.id)          # condizione di join
            & (projection_table.c.id == bindparam('proj_id'))       # la proiezione con id uguale a proj_id
            & (projection_table.c.datetime >= datetime.now())       # solo programmazioni future
        )
        result_set = conn.execute(sel_stmt, proj_id=request.form['proj_id'])
        row = result_set.first()
        if not row:                             # se la query non ha restituito risultati
            abort(404)                          # proiezione non esistente oppure non programmata in futuro
        else:                                   # la proiezione è stata trovata
            movie_title = row['title']          # titolo film
            ticket_price = row['price']         # prezzo biglietto
            ticket_datetime = row['datetime']   # data e ora

    # recupera i metodi di pagamento
    with connect_as(Role.CLIENT) as conn:                           # connessione al database come client
        sel_stmt = select([
            payment_method_table.c.id,
            payment_method_table.c.ownerName,
            payment_method_table.c.cardNumber,
            payment_method_table.c.expirationDate,
            payment_method_table.c.paymentCircuit
        ]).where(
            (payment_method_table.c.user == bindparam('user'))      # solo metodi di pagamento dell'utente loggato
            & (payment_method_table.c.isActive)                     # solo metodi di pagamento attivi
        )
        result_set = conn.execute(sel_stmt, user=current_user.get_id())
        payment_methods = result_set.fetchall()                     # lista metodi di pagamento

    if not error:
        session['seats'] = seats                                # salva lista posti selezionati nella sessione
        total_price = len(seats) * ticket_price                 # calcola prezzo totale
        return render_template('home/checkout.html',            # renderizza riepilogo
                               total_price=total_price,         # prezzo totale
                               title=movie_title,               # titolo film
                               datetime=ticket_datetime,        # data e ora proiezione
                               payment_methods=payment_methods, # metodo di pagamento
                               proj_id=request.form['proj_id'], # id proiezione
                               seats=seats)                     # elenco posti selezionati

    else:                                                                       # in caso di errore
        flash(error ,'warning')                                                 # flasha warning
        return redirect(url_for('home.seats', proj_id=request.form['proj_id'])) # redireziona a selezionatore posti


@bp.route('/confirm_payment_method', methods=('POST',))
@login_required
def confirm_payment_method():
    """Route che permette di inserire CVV o aggiungere metodo di pagamento

    URL: /confirm_payment_method

    La route accetta 1 metodo, POST.
    POST: mostra form per inserire CVV oppure per aggiungere metodo di pagamento

    Returns:
        str: html da renderizzare nel browser
    """

    # recupera i circuiti di pagamento
    with connect_as(Role.CLIENT) as conn:                           # connessione al database come client
        sel_stmt = select([
            payment_circuit_table.c.name
        ])
        result_set = conn.execute(sel_stmt)                         # esegui query
        payment_circuits = [ row['name'] for row in result_set ]    # lista nomi circuiti di pagamento

    proj_id = request.form['proj_id']                               # prendi id proiezione da form
    payment_method_id = request.form['payment-method-id']           # prendi id metodo di pagamento dal form
    if int(payment_method_id) > 0:                                  # metodo di pagamento già registrato
        # mostrare dati metodo di pagamento e chiedere solo cvv

        with connect_as(Role.CLIENT) as conn:                       # connessione al database come client
            # ricava dati metodo di pagamento
            sel_stmt = select([
                payment_method_table
            ]).where(
                (payment_method_table.c.id == bindparam('payment_method_id'))   # metodo di pagamento selezionato
                & (payment_method_table.c.user == bindparam('username'))        # è dell'utente loggato
                & (payment_method_table.c.isActive)                             # metodo di pagamento attivo
            )
            result_set = conn.execute(sel_stmt, payment_method_id=payment_method_id, username=current_user.get_id())
            payment_method = result_set.first()                                 # al più uno (payment_method_id è PK)
            if not payment_method:                                              # se non c'è
                abort(404)                                                      # 404 NOT FOUND

        return render_template('home/add_payment_method.html',          # renderizza form per inserimento CVV
                               payment_method=dict(payment_method),     # dati metodo di pagamento
                               payment_circuits=payment_circuits,       # lista circuiti di pagamento
                               proj_id=proj_id)                         # id proiezione selezionata

    else:                                                               # nuovo metodo di pagamento
        # mostrare form per inserire nuovo metodo di pagamento

        return render_template('home/add_payment_method.html',          # renderizza form per aggiunta metodo di pagamento
                               payment_circuits=payment_circuits,       # lista circuiti di pagamento
                               proj_id=proj_id)                         # id proiezione selezionata


@bp.route('/finalize_payment', methods=('POST',))
@login_required
def finalize_payment():
    """Route che completa l'acquisto dei biglietti

    URL: /finalize_payment

    La route accetta 1 metodo, POST.
    POST: riceve i dati del form (metodo di pagamento) e finalizza l'acquisto

    Returns:
        str: html da renderizzare nel browser
    """

    error = None
    not_available_seats = []

    today = datetime.now().date()                               # data di oggi
    payment_method_id = request.form['payment-method-id']       # prendi id metodo di pagamento dal form

    if int(payment_method_id) == 0:                             # nuovo metodo di pagamento
        # prendi i dati del nuovo metodo di pagamento dal form, inseriscili nel db e porta a termine l'acquisto

        # preleva dati del nuovo metodo di pagamento dal form
        payment_circuit = request.form['payment-circuit']       # circuito di pagamento
        holder_name = request.form['holder-name']               # nome proprietario
        card_number = request.form['card-number']               # numero carta
        expiration = datetime.strptime(request.form.get('expiration', ''), '%Y-%m-%d').date()   # data di scadenza

        # recupera i circuiti di pagamento
        with connect_as(Role.CLIENT) as conn:                   # connessione al database come client
            sel_stmt = select([
                payment_circuit_table.c.name
            ])
            result_set = conn.execute(sel_stmt)
            payment_circuits = [ row['name'] for row in result_set ]    # nomi circuiti di pagamento

        # validazione
        if not payment_circuit:                             # circuito di pagamento mancante
            error = 'Payment circuit required'
        elif payment_circuit not in payment_circuits:       # circuito di pagamento non valido
            error = 'Invalid payment circuit'
        elif not holder_name:                               # nome proprietario mancante
            error = 'Holder name required'
        elif not card_number:                               # numero di carta mancante
            error = 'Card number required'
        elif len(card_number) != 16:                        # numero di carta non valido
            error = 'Invalid card number'
        elif expiration < today:           # metodo di pagamento già scaduto
            error = 'Card already expired'

        # inserimento nuovo metodo di pagamento (con restituzione dell'id della tupla appena inserita)
        with connect_as(Role.CLIENT) as conn:               # connessione al database come client
            ins_stmt = payment_method_table.insert().returning(payment_method_table.c.id)
            result_set = conn.execute(ins_stmt, [{
                'ownerName': holder_name,
                'user': current_user.get_id(),              # username
                'cardNumber': str(card_number),
                'expirationDate': expiration,
                'paymentCircuit': payment_circuit,
                'isActive': True
            }])
            payment_method_id = result_set.first()['id']    # ricava id metodo di pagamento appena inserito


    else:
        # verifica che metodo di pagamento sia dell'utente loggato e sia ancora valido
        with connect_as(Role.CLIENT) as conn:               # connessione al database come client
            sel_stmt = select([
                payment_method_table,
            ]).where(
                (payment_method_table.c.user == bindparam('username'))
                & (payment_method_table.c.id == bindparam('payment_method_id'))
                & (payment_method_table.c.isActive)
            )
            result_set = conn.execute(sel_stmt, username=current_user.get_id(), payment_method_id=payment_method_id)
            payment_method = result_set.first()
            if not payment_method:                          # metodo di pagamento non trovato
                error = 'Invalid payment method'
            elif payment_method['expirationDate'] < today:  # metodo di pagamento scaduto
                error = 'Card already expired'

    # validazione
    cvv = request.form['cvv']
    if not cvv:
        error = 'CVV required'

    if not error:                           # se non ci sono errori
        # prova ad acquistare i biglietti
        error, not_available_seats = try_buy_tickets(payment_method_id, 5)

    return render_template('home/finalize_payment.html',                # renderizza pagina con risultato
                           error=error,                                 # eventuale errore
                           not_available_seats=not_available_seats,     # posti non più disponibili
                           proj_id=request.form['proj_id'])             # id proiezione


@bp.route('/about')
def about():
    """Route che mostra informazioni sul cinema

    URL: /about

    La route accetta 1 metodo, GET.
    GET: mostra informazioni sul cinema

    Returns:
        str: html da renderizzare nel browser
    """

    return render_template('home/about.html')               # renderizza pagina informazioni


def try_buy_tickets(payment_method_id, times=5):
    """Tenta di portare a termine l'acquisto dei biglietti

    Utilizza una transazione con livello di isolamento SERIALIZABLE,
    per tentare di acquistare i biglietti. Se la transazione non va a buon fine,
    perchè i biglietti selezionati sono stati acquistati da qualcun altro, allora
    la funzione restituice un messaggio di errore e l'elenco dei posti non più
    disponibili. Se invece la transazione fallisce non perchè i biglietti non per la
    disponibilità dei biglietti, ma perchè il dbms non è riuscito a portarla a termine
    per motivi interni, allora la funzione riprova ad eseguire la transazione al più per
    'times' volte. Se ancora non è andata a buon fine restituisce un errore.

    Effettua 'times' tentativi di acquisto dei biglietti

    Args:
        payment_method_id (int): id del metodo di pagamento
        times (int): numero di tentativi di portare a termine la transazione,
            a seguito di un eccezione interna del dbms, dopo il quale fermarsi
            e restituire errore (default: 5)

    Returns:
        error (str): messaggio di errore in caso di errore, None altrimenti
        not_available_seats (list): lista di posti non più disponibili;
            esempio di seat: {'row': 1, 'column': 5}
    """

    error = None
    not_available_seats = []

    # connessione al database come client, usando SERIALIZABLE come livello di isolamento
    with connect_as(Role.CLIENT).execution_options(isolation_level="SERIALIZABLE") as conn:
        # tenta di eseguire la transazione al più times volte
        # finché non ha successo, oppure dei biglietti diventano indisponibili
        for iteration in range(times):
            trans = conn.begin()                    # avvia la transazione
            try:
                # seleziona biglietti venduti per la proiezione
                sel_stmt = select([
                    ticket_table.c.row,
                    ticket_table.c.column
                ]).where(
                    (ticket_table.c.purchase == purchase_table.c.id)        # condizione di join
                    & (purchase_table.c.projection == bindparam('proj_id')) # biglietti della proiezione selezionata
                )
                result_set = conn.execute(sel_stmt, proj_id=request.form['proj_id'])

                selected_seats = session['seats']                           # elenco posti selezionati per l'acquisto

                # verifica che posti scelti siano disponibili
                not_available_seats = []                                    # elenco psoti non disponibili
                for ticket in result_set:                                   # per ogni biglietto venduto
                    for seat in selected_seats:                             # per ogni posto selezionato
                        if seat['row'] == ticket['row'] and seat['column'] == ticket['column']:
                            not_available_seats.append(seat)                # se il posto è già stato venduto
                                                                            # aggiungilo alla lista

                if len(not_available_seats) > 0:                            # se ci sono posti non più disponibili
                    error = 'Some seats are no longer available :('
                    raise                                                   # solleva eccezione

                # calcola prezzo
                sel_stmt = select([
                    projection_table.c.price                                # seleziona il prezzo
                ]).where(
                    (projection_table.c.id == bindparam('proj_id'))         # la proiezione con id uguale a proj_id
                    & (projection_table.c.datetime >= datetime.now())       # solo programmazioni future
                )
                result_set = conn.execute(sel_stmt, proj_id=request.form['proj_id'])
                row = result_set.first()
                if not row:                                                 # se la query non ha restituito risultati
                    error = 'Chosen projection does not exist or is already past'
                    raise                                                   # solleva eccezione
                else:                                                       # il prezzo della proiezione è stato trovato
                    ticket_price = row['price']

                # pagamento (fake)
                # done = do_payment()
                done = True

                if not done:                                                # in caso di errore nella fase di pagamento
                    error = 'Payment error: try again later'
                    raise                                                   # solleva eccezione

                # inserimento acquisto (con restituzione del id della tupla inserita)
                ins_stmt = purchase_table.insert().returning(purchase_table.c.id)
                result_set = conn.execute(ins_stmt, [{
                    'projection': request.form['proj_id'],          # id proiezione
                    'total': len(selected_seats) * ticket_price,    # calcolo prezzo
                    'purchaseDatetime': datetime.now(),             # data corrente
                    'paymentMethod': payment_method_id              # id metodo di pagamento
                }])
                purchase_id = result_set.first()['id']              # id acquisto appena inserito

                # inserimento biglietti
                tickets = [                                         # crea lista tuple da inserire (una per biglietto)
                    { 'row': seat['row'], 'column': seat['column'], 'purchase': purchase_id }
                    for seat in selected_seats
                ]
                ins_stmt = ticket_table.insert()
                conn.execute(ins_stmt, tickets)

                trans.commit()                                      # transazione andata a buon fine: commit
                break                                               # esci dal ciclo

            except:
                trans.rollback()                                    # transazione fallita: rollback

                if not error:                                       # se ad error non è ancora stato assegnato niente
                    error = 'Transaction error'                     # allora significa che è un errore del dbms

                current_app.logger.info('Transaction rolled back (id: %s): %s [%s]',    # logga errore
                                        iteration,                  # numero iterazione
                                        error,                      # messaggio di errore
                                        current_user.get_id())      # username

                if error != 'Transaction error':
                    break                                           # non è colpa del dbms, non ha senso riprovare

            time.sleep(random.uniform(0.03, 0.13))                  # random delay

    return error, not_available_seats           # restituisce eventuale errore e list aposti non più disponibili
