import os

import pytest

from app import create_app


@pytest.fixture
def app():
    """Genera una nuova Flask app configurata per il testing"""
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': os.getenv('SECRET_KEY')
    })

    return app


@pytest.fixture
def client(app):
    """Genera un client per il testing"""
    return app.test_client()                    # restituisce un client di test generato da flask



class AuthActions(object):
    """Classe wrapper per un client che è in grado di loggarsi"""

    def __init__(self, client):
        self._client = client

    def login(self, email='test@gmail.com', password='test'):
        return self._client.post(
            '/auth/login',
            data={'email': email, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')


@pytest.fixture
def auth(client):
    return AuthActions(client)
