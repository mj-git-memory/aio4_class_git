"""Import from the PythonAnywhere Web tab's WSGI configuration."""
from app import create_app

application = create_app()
application.config.update(SESSION_COOKIE_SECURE=True, DEBUG=False)
if not application.config.get('SECRET_KEY'):
    raise RuntimeError('먼저 flask --app app init-config로 영속 비밀 설정을 생성하세요.')
