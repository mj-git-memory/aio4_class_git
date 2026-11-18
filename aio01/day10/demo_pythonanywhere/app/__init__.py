import os
import sqlite3
from datetime import timedelta
from pathlib import Path

from flask import Flask, g, jsonify, render_template, request, session
from flask_wtf.csrf import CSRFError, CSRFProtect
from werkzeug.exceptions import HTTPException

csrf = CSRFProtect()


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=None,
        DATABASE=str(Path(app.instance_path) / 'note_demo.sqlite3'),
        MAX_CONTENT_LENGTH=64 * 1024,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=False,
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8),
        WTF_CSRF_TIME_LIMIT=8 * 60 * 60,
    )
    app.config.from_pyfile('config.py', silent=True)
    if test_config:
        app.config.update(test_config)
    if not Path(app.config['DATABASE']).is_absolute():
        raise ValueError('DATABASE는 절대 경로여야 합니다.')
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)

    from . import auth, admin, db, guestbook
    db.init_app(app)

    @app.before_request
    def load_user():
        g.user = None
        if not app.config['SECRET_KEY']:
            return render_template('error.html', message='먼저 init-config와 init-db 명령으로 앱을 준비해 주세요.'), 503
        if session.get('user_id'):
            g.user = db.get_db().execute(
                'SELECT id, email, nickname, role FROM users WHERE id = ?',
                (session['user_id'],),
            ).fetchone()
            if not g.user:
                session.clear()

    csrf.init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(guestbook.bp)
    app.register_blueprint(admin.bp)

    def error_response(message, status):
        if request.path.startswith('/api/'):
            return jsonify(error=message), status
        return render_template('error.html', message=message), status

    @app.errorhandler(CSRFError)
    def csrf_error(error):
        return error_response('요청 확인 시간이 지났거나 보안 토큰이 없습니다. 새로고침 후 다시 시도해 주세요.', 400)

    @app.errorhandler(HTTPException)
    def http_error(error):
        messages = {400: '입력값을 확인해 주세요.', 401: '로그인이 필요합니다.',
                    403: '이 작업을 수행할 권한이 없습니다.', 404: '대상을 찾을 수 없습니다.',
                    405: '허용하지 않는 요청 방식입니다.', 413: '입력 크기가 너무 큽니다.'}
        return error_response(messages.get(error.code, '요청을 처리하지 못했습니다.'), error.code)

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        app.logger.error('SQLite 요청 실패: %s', type(error).__name__)
        return error_response('데이터 저장소를 사용할 수 없습니다. 초기화 여부 또는 관리자 백업·복구 안내를 확인해 주세요.', 503)

    @app.after_request
    def response_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; object-src 'none'; base-uri 'self'; "
            "form-action 'self'; frame-ancestors 'none'"
        )
        if request.endpoint != 'static':
            response.headers['Cache-Control'] = 'no-store'
        return response

    return app
