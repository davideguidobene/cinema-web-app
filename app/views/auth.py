"""
Modulo contenente le route della fase di autenticazione.
Le route sono registrate nel Blueprint 'auth', con prefisso '/auth'.
"""

from datetime import date, datetime
import functools

from flask import (
    Blueprint, request, current_app, redirect, url_for, flash, render_template, g, abort
)
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import bindparam
from werkzeug.security import generate_password_hash, check_password_hash
from is_safe_url import is_safe_url

from app.models.db import connect_as, Role
from app.models.db import user_table
from app.models.db import User
from app.utils.utils import valid_email


bp = Blueprint('auth', __name__, url_prefix='/auth')    # Blueprint per le route di autenticazione


@bp.route('/register', methods=('GET', 'POST'))
def register():
    """Route che gestisce la registrazione

    URL: /register

    La route accetta 2 metodi, GET e POST.
    GET: restituisce il form di registrazione
    POST: preleva i dati dal form di registrazione, li valida
        e poi effettua l'inserimento del nuovo utente nel database.

    Returns:
        str: html da renderizzare nel browser
    """

    if request.method == 'POST':                # POST -> form i registrazione inviato
        # preleva i dati dal form
        username = request.form.get('username', None)
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        name = request.form.get('name', None)
        surname = request.form.get('surname', None)
        birthdate = datetime.strptime(request.form.get('birthdate', ''), '%Y-%m-%d').date()

        # validazione input
        error = None
        if not username:                        # username mancante
            error = 'Username required'
        elif not email:                         # email mancante
            error = 'Email required'
        elif not password:                      # password mancante
            error = 'Password required'
        elif not name:                          # nome mancante
            error = 'Name required'
        elif not surname:                       # cognome mancante
            error = 'Surname required'
        elif not birthdate:                     # data di nascita mancante
            error = 'Birthdate required'
        elif birthdate > date.today():          # data di nascita futura
            error = 'Birthdate not valid'
        elif not valid_email(email):            # email non valida
            error = 'Email not valid'
        else:
            # inserimento del nuovo utente nel database
            with connect_as(Role.CLIENT) as conn:               # connessione al database come client
                try:
                    # verifica che username e email non siano già registrati
                    sel_stmt = select([
                        user_table.c.username,
                        user_table.c.email
                    ]).where(
                        (user_table.c.username == bindparam('username'))    # stesso username
                        | (user_table.c.email == bindparam('email'))        # o stessa email
                    )
                    results = conn.execute(sel_stmt, username=username, email=email)
                    row = results.first()                                   # al più un utente
                    if row:
                        if username == row['username']:                     # username già registrato
                            error = f'Username {username} already registered'
                        else:                                               # email già registrata
                            error = f'Email {email} already registered'
                        raise

                    ins_stmt = user_table.insert().values(
                        username=bindparam('username'),
                        email=bindparam('email'),
                        password=bindparam('password'),
                        name=bindparam('name'),
                        surname=bindparam('surname'),
                        birthdate=bindparam('birthdate'),
                        registrationDate=bindparam('registrationDate'),
                        isOperator=bindparam('isOperator')
                    )

                    conn.execute(
                        ins_stmt,
                        username=username,
                        email=email,
                        password=generate_password_hash(password),
                        name=name,
                        surname=surname,
                        birthdate=birthdate,
                        registrationDate=datetime.now().date(),
                        isOperator=False
                    )

                except:
                    if not error:       # IntegrityError
                        # un nuovo utente si è registrato nel fattempo con gli stessi username o password
                        error = 'Username {username} or {email} already registered'

        if not error:                                   # nessun problema: utente registrato
            current_app.logger.info('Registration succeded: %s', username)
            return redirect(url_for('auth.login'))      # ridirezione alla view di login

        # errore di registrazione
        current_app.logger.info('Registration failed: %s', error)
        flash(error, 'danger')                          # flasha l'errore sulla pagina di registrazione

    # GET o errore di registrazione
    return render_template('auth/register.html')        # renderizza pagina con form di registrazione


@bp.route('/login', methods=('GET', 'POST'))
def login():
    """Route che gestisce il login

    URL: /login

    La route accetta 2 metodi, GET e POST.
    GET: restituisce il form di login
    POST: preleva i dati dal form di login e li valida
        verificando se sono corretti.

    Returns:
        str: html da renderizzare nel browser
            (home page o route da cui utente proveniva)
    """

    if current_user.is_authenticated:                       # utente già autenticato
        return redirect(url_for('home.home'))               # redirezione alla home page

    if request.method == 'POST':                            # POST -> form di login inviato
        # preleva i dati dal form
        email = request.form.get('email', None)
        password = request.form.get('password', None)
        remember_me = bool(request.form.get('remember-me', default=False))

        # validazione input e controllo email e password corretti
        error = None
        if not email:                                       # email mancante
            error = 'Email required'
        elif not password:                                  # password mancante
            error = 'Password required'
        else:
            with connect_as(Role.CLIENT) as conn:           # connessione al database come client
                # seleziona password dell'utente con email data
                sel_stmt = select([
                    user_table.c.password
                ]).where(
                    user_table.c.email == bindparam('email')            # utente con email data
                )
                results = conn.execute(sel_stmt, email=email)
                row = results.first()                                   # al più un utente
                hashed_password = row['password'] if row else None      # preleva password hashata

            if not hashed_password:                                     # utente non trovato
                error = f'Email {email} not registered'
            elif not check_password_hash(hashed_password, password):    # hash delle password non matchano
                error = 'Incorrect password'

        if not error:                                                   # login è andato a buon fine
            user = user_by_email(email)                                 # ottieni Flask-Login User tramite email
            login_user(user, remember=remember_me)                      # effettua il login dell'utente
            current_app.logger.info('Login succeded: %s', user.get_id())

            # verifica se utente va redirezionato ad un particolare url (sicuro)
            # in generale all'url da cui proveniva
            next_url = request.args.get('next', None)                   # parametro 'next'
            if next_url and not is_safe_url(next_url, { 'localhost' }): # verifica sicurezza url
                current_app.logger.info('Attempt to redirect to an unsafe url: %s', next_url)
                abort(400)                                              # errore 400 BAD REQUEST

            return redirect(next_url or url_for('home.home'))           # redireziona utente a pagina corretta

        # errore di login
        current_app.logger.info('Login failed: %s', error)
        flash(error, 'danger')                                          # flasha l'errore sulla pagina di login

    # GET o errore di login
    return render_template('auth/login.html')                           # renderizza pagina con form di registrazione


@bp.route('/logout')
def logout():
    """Route che gestisce il logout

    URL: /logout

    La route accetta 1 metodo, GET.
    GET: effettua il logout dell'utente

    Returns:
        str: html da renderizzare nel browser (home page)
    """

    user_username = current_user.get_id()                       # salva username dell'utente
    logout_user()                                               # esegue il logout dell'utente

    current_app.logger.info('Logout: %s', user_username)        # logga il logout dell'utente

    return redirect(url_for('home.home'))                       # redireziona l'utente alla home page


def user_by_email(email):
    """Restituisce un User Flask-Login a partire dall'email

    Args:
        email (str): l'email dell'utente da selezionare

    Returns:
        User: un nuovo utente della classe User di Flask-Login se
            esiste nel database un utente con email 'email',
            altrimenti None
    """

    # seleziona le informazioni sull'utente con email data, dal database
    with connect_as(Role.CLIENT) as conn:                   # connessione al database come client
        sel_stmt = select([
            user_table.c.username,
            user_table.c.email,
            user_table.c.name,
            user_table.c.surname,
            user_table.c.isOperator
        ]).where(
            user_table.c.email == bindparam('email')        # campo email uguale all'email dato
        )
        result_set = conn.execute(sel_stmt, email=email)    # esegue statement
        user = result_set.first()                           # al più un utente (email è UNIQUE)

    return User(user['username'],                           # crea e restituisce Flask-Login User
                user['email'],
                user['name'],
                user['surname'],
                user['isOperator']) if user else None       # se non è presente restituisce None


def operator_required(view):                        # view: funzione decorata da @operator_required
    """Decoratore che si assicura che l'utente sia loggato e sia un operatore"""
    @functools.wraps(view)
    @login_required                                 # autenticazione necessaria per accedere alla view
    def wrapped_view(**kwargs):
        if not current_user.is_operator:            # se non è un operatore
            return abort(403)                       # 403 Forbidden
        else:
            return view(**kwargs)                   # restituisce l'html prodotto dalla view

    return wrapped_view                             # view decorata
