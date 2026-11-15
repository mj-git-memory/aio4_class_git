def pytest_addoption(parser):
    parser.addoption('--test-db', default=None, help='로컬 _test DB DSN. 운영 DB 금지')
