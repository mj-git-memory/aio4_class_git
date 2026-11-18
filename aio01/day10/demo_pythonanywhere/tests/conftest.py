import re

import pytest

from app import create_app


@pytest.fixture
def app(tmp_path):
    application = create_app({'TESTING': True, 'SECRET_KEY': 'tests-only-not-for-deployment',
                              'DATABASE': str(tmp_path / 'test.sqlite3')})
    result = application.test_cli_runner().invoke(args=['init-db'])
    assert result.exit_code == 0, result.output
    return application


@pytest.fixture
def client(app):
    return app.test_client()


def token(client):
    html = client.get('/').get_data(as_text=True)
    return re.search(r'name="csrf-token" content="([^"]+)"', html).group(1)


def signup(client, email='one@example.com', nickname='첫회원'):
    return client.post('/signup', data={'email': email, 'nickname': nickname, 'password': 'test-password', 'csrf_token': token(client)})


def login(client, email='one@example.com'):
    return client.post('/login', data={'email': email, 'password': 'test-password', 'csrf_token': token(client)})


def api(client, path, method='GET', data=None):
    return client.open(path, method=method, json=data, headers={'X-CSRFToken': token(client)})


@pytest.fixture
def member(client):
    assert signup(client).status_code == 302
    assert login(client).status_code == 302
    return client
