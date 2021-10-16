import pytest


@pytest.mark.parametrize('path', (
    '/seats/1',
))
def test_login_required(client, path):
    """Test @login_required"""
    response = client.get(path)
    assert '/auth/login' in response.headers['Location']


def test_index(client, app):
    """Test / route"""

    response = client.get('/')
    assert response.status_code == 200


def test_movies(client, app):
    """Test /movies route"""

    response = client.get('/movies')
    assert response.status_code == 200


def test_movies_id(client, app):
    """Test /movies/movie_id route"""

    response = client.get('/movies/ciao')
    assert response.status_code == 404

    response = client.get('/movies/1')
    assert response.status_code == 200

    response = client.get('/movies/2')
    assert response.status_code == 200


def test_seats(client, auth):
    """Test /seats route"""

    # verifica che la route /seats senza id proiezione non sia raggiungibile
    response = client.get('/seats')
    assert response.status_code == 404

    # verifica che la route /seats/1 sia raggiungibile, ma non utilizzabile da un'utente non loggato
    response = client.get('/seats/1')
    assert response.status_code == 302
    assert b'Redirecting' in response.data

    # verifica che la route /seats/1 sia raggiungibile ed utilizzabile da un utente loggato
    auth.login()
    response = client.get('/seats/1')
    assert response.status_code == 200
    assert b'Seleziona posti' in response.data              # verifica ridirezione a pagina di login


def test_about(client, app):
    """Test /about route"""

    response = client.get('/about')
    assert response.status_code == 200
