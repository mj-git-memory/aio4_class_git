"""API의 계산과 오류 처리 검증. 외부 서버 없이 실행한다."""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


@pytest.mark.parametrize(('a', 'b', 'expected'), [
    ('12', '4', ('16', '8', '48', '3')),
    ('-3', '2', ('-1', '-5', '-6', '-1.5')),
    ('0.1', '0.2', ('0.3', '-0.1', '0.02', '0.5')),
    ('1', '3', ('4', '-2', '3', '0.3333333333')),
    ('2', '3', ('5', '-1', '6', '0.6666666667')),
    ('0', '-2', ('-2', '2', '0', '0')),
])
def test_arithmetic(a, b, expected):
    response = client.post('/api/calculate', json={'a': a, 'b': b})
    assert response.status_code == 200
    data = response.json()
    assert tuple(data[key] for key in ('addition', 'subtraction', 'multiplication', 'division')) == expected
    assert data['division_error'] is None


def test_zero_division_preserves_other_results():
    response = client.post('/api/calculate', json={'a': '7', 'b': '0'})
    data = response.json()
    assert response.status_code == 200
    assert (data['addition'], data['subtraction'], data['multiplication']) == ('7', '7', '0')
    assert data['division'] is None
    assert data['division_error'] == '0으로는 나눌 수 없어요.'


@pytest.mark.parametrize('body', [
    {}, {'a': '1'}, {'a': '', 'b': '2'}, {'a': 'abc', 'b': '2'},
    {'a': None, 'b': '2'}, {'a': 'NaN', 'b': '2'},
    {'a': 'Infinity', 'b': '2'}, {'a': '0.12345678901', 'b': '2'},
    {'a': '1234567890123456789012345678901', 'b': '2'},
])
def test_invalid_input(body):
    assert client.post('/api/calculate', json=body).status_code == 422


def test_large_multiplication_is_exact():
    value = '99999999999999999999'
    response = client.post('/api/calculate', json={'a': value, 'b': value})
    assert response.status_code == 200
    assert response.json()['multiplication'] == str(int(value) ** 2)


def test_page_and_assets():
    assert '두 숫자 계산기' in client.get('/').text
    for path in ('/static/style.css', '/static/app.js', '/docs'):
        assert client.get(path).status_code == 200
