import pytest


def test_register(client, app):
    """Testa /auth/register"""

    assert client.get('/auth/register').status_code == 200


def test_login(client):
    """Testa /auth/login"""

    assert client.get('/auth/login').status_code == 200


def test_logout(client):
    """Testa /auth/logout"""

    pass
