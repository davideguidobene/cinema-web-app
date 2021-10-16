"""
Modulo contenente le route dell'area riservata.
Le route sono registrate nel Blueprint 'reserved_area', con prefisso '/auth'.
"""

from datetime import date, datetime

from flask import Blueprint, redirect, url_for, render_template, abort, request
from flask_login import current_user, login_required
from sqlalchemy.sql import select, desc
from sqlalchemy.sql.expression import bindparam, func
from werkzeug.security import generate_password_hash

from app.models.db import connect_as, Role
from app.models.db import (
    projection_table, purchase_table, ticket_table,
    payment_method_table, movie_table, user_table
)


bp = Blueprint('reserved_area', __name__, url_prefix='/reserved_area')  # Blueprint per le route dell'area riservata


def check_permissions(table, key):
    """Controlla che l'utente corrente abbia i permessi per accedere alla pagina

    Se non ha i permessi, l'utente viene redirezionato ad una pagina di errore.

    Pre:
        - table ha una foreigner_key username verso user_table
        - id dev'essere la primary key di table

    Args:
        table (Table): table ha una foreigner_key username verso user_table
        key (str): valore della primary key di table
    """

    username = current_user.get_id()

    # seleziona tupla con chiave key
    select_related_user = select([
        table.c.user
    ]).where(
        table.c.id == bindparam('key')
    )

    with connect_as(Role.CLIENT) as conn:                   # connessione al database come client
        related_user = conn.execute(select_related_user, key=key)
        user = related_user.first()
        if not user:                                        # tupla non esiste
            abort(404)                                      # 404 NOT FOUND
        if user['user'] != username:                        # username non matcha
            abort(403)                                      # 403 FORBIDDEN


@bp.route('/')
@login_required
def reserved_area():
    """Route che renderizza l'area riservata

    URL: /

    La route accetta 1 metodo, GET.
    GET: restituisce l'area riservata

    Returns:
        str: html da renderizzare nel browser
    """

    return render_template('reserved_area/index.html')


@bp.route('/purchase_history')
@login_required
def purchase_history():
    """Route che mostra elenco acquisti utente

    URL: /purchase_history

    La route accetta 1 metodo, GET.
    GET: restituisce la pagina con l'elenco degli acquisti

    Returns:
        str: html da renderizzare nel browser
    """

    username = current_user.get_id()

    # seleziona lo storico degli acquisti dell'utente loggato
    select_purchase_history_stmt = select([
        purchase_table.c.id,
        movie_table.c.title.label('movie_title'),
        projection_table.c.datetime.label('proj_datetime'),
        purchase_table.c.total,
        func.count(ticket_table.c.id).label('ticket_count')                 # conteggio biglietti in ogni acquisto
    ]).where(
        (payment_method_table.c.user == bindparam('username'))              # acquisti dell'utente
        & (purchase_table.c.paymentMethod == payment_method_table.c.id)     # condizione di join
        & (projection_table.c.id == purchase_table.c.projection)            # condizione di join
        & (ticket_table.c.purchase == purchase_table.c.id)                  # condizione di join
        & (movie_table.c.id == projection_table.c.movie)                    # condizione di join
    ).group_by(
        purchase_table.c.id,                            # raggruppa per id acquisto
        movie_table.c.title,                            # necessario per soddisfare SQL (non raggruppa di più)
        projection_table.c.datetime                     # necessario per soddisfare SQL (non raggruppa di più)
    ).order_by(
        desc(purchase_table.c.purchaseDatetime)         # gli acquisti più recenti per primi
    )

    with connect_as(Role.CLIENT) as conn:               # connessione al database come client
        purchase_history = conn.execute(select_purchase_history_stmt, username=username)

    # restituisce la pagina con l'elenco degli acquisti
    return render_template('reserved_area/purchase_history.html', purchase_history=purchase_history)


@bp.route('/purchase_history/<int:purchase_id>')
@login_required
def purchase_details(purchase_id):
    """Route che mostra i dettagli dell'acquisto 'purchase_id'

    URL: /purchase_history/<int:purchase_id>

    La route accetta 1 metodo, GET.
    GET: restituisce la pagina con i dettagli dell'acquisto

    Args:
        purchase_id (int): id dell'acquisto

    Returns:
        str: html da renderizzare nel browser
    """

    # seleziona dettagli acquisto
    sel_purchase_details_stmt = select([
        purchase_table.c.id                  .label('purchase_id'),
        purchase_table.c.total               .label('purchase_total'),
        purchase_table.c.purchaseDatetime    .label('purchase_datetime'),
        payment_method_table.c.ownerName     .label('payment_method_holder_name'),
        payment_method_table.c.cardNumber    .label('payment_method_card_number'),
        payment_method_table.c.paymentCircuit.label('payment_circuit'),
        payment_method_table.c.isActive      .label('payment_method_active'),
        projection_table.c.room              .label('room'),
        projection_table.c.datetime          .label('proj_datetime'),
        projection_table.c.price             .label('proj_price'),
        movie_table.c.title                  .label('movie_title')
    ]).where(
        (purchase_table.c.id == bindparam('purchase_id'))
        & (payment_method_table.c.user == bindparam('username'))
        & (purchase_table.c.paymentMethod == payment_method_table.c.id) # condizione di join
        & (purchase_table.c.projection == projection_table.c.id)        # condizione di join
        & (projection_table.c.movie == movie_table.c.id)                # condizione di join
    )

    # seleziona biglietti acquisto
    sel_tickets_stmt = select([
        ticket_table.c.row,
        ticket_table.c.column
    ]).where(
        (ticket_table.c.purchase == bindparam('purchase_id'))
    )

    with connect_as(Role.CLIENT) as conn:                   # connessione al database come client
        result_set = conn.execute(sel_purchase_details_stmt, purchase_id=purchase_id, username=current_user.get_id())
        purchase_details = result_set.first()               # al più uno
        tickets = conn.execute(sel_tickets_stmt, purchase_id=purchase_id)

    # verifica che acquisto sia stato fatto da utente loggato
    if not purchase_details:
        abort(404)

    # se il metodo di pagamento è stato cancellato dall'utente (isActive == False), non mostrarne più i dettagli
    purchase_details = dict(purchase_details)       # trasforma RowProxy in dict, perchè RowProxy non supporta assegnamento
    if not purchase_details['payment_method_active']:
        purchase_details['payment_method_holder_name'] = 'No longer available'
        purchase_details['payment_method_card_number'] = 'No longer available'
        purchase_details['payment_circuit'] = 'No longer available'

    # restituisce pagina dettagli acquisto
    return render_template('reserved_area/purchase_details.html', purchase_details=purchase_details, tickets=tickets)


@bp.route('/payment_methods')
@login_required
def payment_methods():
    """Route che mostra i metodi di pagamento dell'utente

    URL: /payment_methods

    La route accetta 1 metodo, GET.
    GET: restituisce la pagina con l'elenco dei metodi di pagamento dell'utente

    Returns:
        str: html da renderizzare nel browser
    """

    username = current_user.get_id()                                # username dell'utente loggato

    # seleziona metodi di pagamento
    select_payment_methods_stmt = select([
        payment_method_table
    ]).where(
        (payment_method_table.c.user == bindparam('username'))      # solo quelli dell'utente loggato
        & (payment_method_table.c.isActive)                         # solo quelli attivi
    )

    with connect_as(Role.CLIENT) as conn:
        payment_methods = conn.execute(select_payment_methods_stmt, username=username)

    return render_template('reserved_area/payment_methods.html', payment_methods=payment_methods)


@bp.route('/payment_methods/remove/<int:payment_method_id>')
@login_required
def remove_payment_method(payment_method_id):
    """Route che rimuove il metodo di pagamento con id 'payment_method_id'

    URL: /payment_methods/remove/<int:payment_method_id>

    La route accetta 1 metodo, GET.
    GET: rimuove il metodo di pagamento e ridireziona all'elenco
        dei metodi di pagamento

    Returns:
        str: html da renderizzare nel browser
    """

    # verifica che il metodo di pagamento sia dell'utente
    check_permissions(payment_method_table, payment_method_id)

    # disattiva metodo di pagamento (isActive <- False)
    update_payment_method_stmt = payment_method_table.update().where(
        payment_method_table.c.id == bindparam('payment_method_id')
    ).values(isActive=False)

    with connect_as(Role.CLIENT) as conn:                   # connessione al database come client
        conn.execute(update_payment_method_stmt, payment_method_id=payment_method_id)

    # redirezione alla pagina con l'elenco dei metodi di pagamento
    return redirect(url_for('reserved_area.payment_methods'))


@bp.route('/settings', methods=('GET', 'POST'))
@login_required
def settings():
    """Route che permette all'utente di vedere e aggiornare propri dati

    URL: /settings

    La route accetta 2 metodi, GET e POST.
    GET: mostra informazioni utente con un form
    POST: modifica dati utente presi dal form

    Returns:
        str: html da renderizzare nel browser
    """

    username = current_user.get_id()                                # username dell'utente loggato

    if request.method == 'POST':                                    # POST -> update
        column_names = [ col.name for col in user_table.columns ]   # lista nomi colonne
        # per ogni campo del form con nome uguale al nome di un attributo della tabella selezionata
        # inserisce una entry nel dizionario (nome_attributo, valore_attributo)
        # di fatto genera una tupla con gli attributi corretti per il database
        new_tuple = { key: value for key, value in request.form.items() if key in column_names }

        # aggiusta la tupla per il database
        if new_tuple['password']:                                   # se user ha inserito anche password
            new_tuple['password'] = generate_password_hash(new_tuple['password'])   # hash password
        else:
            del new_tuple['password']                               # altrimenti elimina il campo dal dizionario
                                                                    # in modo da non aggiornarlo nel database
        new_tuple['birthdate'] = datetime.strptime(new_tuple['birthdate'], '%Y-%m-%d').date()   # aggiusta la data per il database

        # aggiorna tupla nel database
        update_user_stmt = user_table.update().where(
            user_table.c.username == bindparam('username_')     # dove chiave primaria è username dell'utente loggato
        ).values(**new_tuple)

        with connect_as(Role.CLIENT) as conn:                   # connessione al database come client
            conn.execute(update_user_stmt, username_=username)

        # redireziona alla pagina di logout per applicare i cambiamenti
        return redirect(url_for('auth.logout'))

    else:                                                       # GET -> mostra dati utente
        # seleziona dati utente loggato
        select_user_stmt = select([
            user_table
        ]).where(
            user_table.c.username == bindparam('username')      # username dell'utente loggato
        )

        with connect_as(Role.CLIENT) as conn:                   # connessione al database come client
            result_set = conn.execute(select_user_stmt, username=username)
            tuple_ = dict(result_set.first())                   # trasforma RowProxy in dict (html si aspetta dict)

        # restituisce pagina delle impostazioni, con dati utente
        return render_template('reserved_area/settings.html', tuple=tuple_)
