"""
Crea e configura l'applicazione Flask e dice a python che la cartelle app deve essere trattata come un package.
"""

import os

from flask import Flask
from flask_login import LoginManager
from sqlalchemy.sql import select
from sqlalchemy.sql.expression import bindparam

from app.models.db import connect_as, Role
from app.models.db import user_table
from app.utils.utils import shorten_text


def create_app(test_config=None):
    """Crea e configura l'applicazione Flask

    Args:
        test_config: configurazione alternativa per i test automatici
            (default: None)

    Returns:
        app: una nuova applicazione Flask configurata
    """

    app = Flask(                                        # crea app Flask
        __name__,
        instance_path=os.path.abspath('instance'),      # configura cartella per dati che non dovrebbero essere
        instance_relative_config=True                   # committati nel sistema di version control
    )


    # carica la configurazione richiesta
    if not test_config:
        app.config.from_pyfile('config.py')             # carica configurazione da variabili d'ambiente
    else:
        app.config.from_mapping(test_config)            # carica configurazione per test


    # aggiunta utili funzioni python all'ambiente di Jinja (ovvero ai template)
    app.jinja_env.globals.update(zip=zip)
    app.jinja_env.globals.update(enumerate=enumerate)
    app.jinja_env.globals.update(str=str)
    app.jinja_env.globals.update(shorten_text=shorten_text)     # funzione per troncare testo troppo lungo


    # configurazione Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'                 # imposta pagina di login
    login_manager.login_message = u'Please log in to access this page'      # messaggio di errore
    login_manager.login_message_category = 'warning'        # categoria messaggi flash
    login_manager.init_app(app)                             # inizializza Flask app per Flask-Login

    from app.models.db import User                          # importa classe User per Flask-Login

    @login_manager.user_loader
    def load_user(username):                                # user_loader callback per Flask-Login
        """Funzione usata come callback da Flask-Login per la fase di autenticazione

        Args:
            username (str): l'username dell'utente

        Returns:
            User: un nuovo utente della classe User di Flask-Login se
                esiste nel database un utente con username 'username',
                altrimenti None
        """

        with connect_as(Role.CLIENT) as conn:                       # connessione al database come client
            # seleziona le informazioni sull'utente con username dato, dal database
            sel_stmt = select([
                user_table.c.username,
                user_table.c.email,
                user_table.c.name,
                user_table.c.surname,
                user_table.c.isOperator
            ]).where(
                user_table.c.username == bindparam('username')      # campo username uguale all'username dato
            )
            result_set = conn.execute(sel_stmt, username=username)  # esegue statement
            user = result_set.first()                               # al più un utente (username è PK)

        return User(user.username,                                  # crea e restituisce Flask-Login User
                    user.email,
                    user.name,
                    user.surname,
                    user.isOperator) if user else None              # se non è presente restituisce None


    # importa i moduli contenenti le views
    from .views import home
    app.register_blueprint(home.bp)                         # registra home blueprint

    from .views import auth
    app.register_blueprint(auth.bp)                         # registra auth blueprint

    from .views import dash
    app.register_blueprint(dash.bp)                         # registra dash blueprint

    from .views import reserved_area
    app.register_blueprint(reserved_area.bp)                # registra reserved_area blueprint


    return app                                              # Flask app
