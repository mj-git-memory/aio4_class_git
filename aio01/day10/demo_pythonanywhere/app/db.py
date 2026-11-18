import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def new_id():
    return str(uuid4())


def now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds')


def connect(path, create=False):
    # A read/write request must never create a replacement for a missing DB.
    uri = Path(path).as_uri() + ('?mode=rwc' if create else '?mode=rw')
    connection = sqlite3.connect(uri, uri=True, timeout=3)
    connection.row_factory = sqlite3.Row
    connection.execute('PRAGMA foreign_keys = ON')
    return connection


def get_db():
    if 'db' not in g:
        g.db = connect(current_app.config['DATABASE'])
    return g.db


def close_db(error=None):
    connection = g.pop('db', None)
    if connection:
        connection.close()


@click.command('init-config')
@with_appcontext
def init_config():
    """Create a persistent secret without printing it or overwriting config."""
    path = Path(current_app.instance_path) / 'config.py'
    try:
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        raise click.ClickException('instance/config.py가 이미 있습니다. 기존 설정을 유지합니다.')
    with os.fdopen(fd, 'w', encoding='utf-8') as handle:
        handle.write('SECRET_KEY = ' + repr(secrets.token_hex(32)) + '\n')
    click.echo('instance/config.py 생성 완료. 비밀 키를 공개하지 마세요.')


@click.command('init-db')
@with_appcontext
def init_db():
    """Initialize once; never repopulate rules removed by the administrator."""
    path = Path(current_app.config['DATABASE'])
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = connect(path, create=True)
    try:
        version = connection.execute('PRAGMA user_version').fetchone()[0]
        tables = connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        if version == 1:
            click.echo('이미 초기화된 DB입니다. 데이터와 규칙을 유지합니다.')
            return
        if version != 0 or tables:
            raise click.ClickException('알 수 없는 DB 구조입니다. 백업 후 스키마를 확인하세요.')
        connection.executescript((Path(__file__).parent / 'schema.sql').read_text(encoding='utf-8'))
        seeds = json.loads((Path(__file__).parent / 'data' / 'initial_rules.json').read_text(encoding='utf-8'))
        for rule in seeds['rules']:
            connection.execute('INSERT INTO masking_rules VALUES (?, ?, ?, ?, ?)',
                               (new_id(), rule['type'], rule['pattern'], rule.get('flags', ''), now()))
        connection.commit()
        click.echo('DB 스키마 v1 및 초기 마스킹 규칙 생성 완료.')
    except sqlite3.Error:
        connection.rollback()
        raise click.ClickException('DB 초기화 실패. 기존 파일을 삭제하지 말고 구조·권한·백업을 확인하세요.')
    finally:
        connection.close()


@click.command('create-admin')
@click.option('--email', prompt='관리자 이메일')
@click.option('--nickname', prompt='관리자 닉네임')
@click.option('--password', prompt='관리자 비밀번호', hide_input=True, confirmation_prompt=True)
@with_appcontext
def create_admin(email, nickname, password):
    from .auth import validate_signup
    try:
        email, nickname = validate_signup(email, nickname, password)
    except ValueError as error:
        raise click.ClickException(str(error))
    db = get_db()
    try:
        with db:
            db.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)',
                       (new_id(), email, nickname, generate_password_hash(password, method='pbkdf2:sha256:600000'), 'admin', now()))
    except sqlite3.IntegrityError:
        raise click.ClickException('이미 등록된 이메일입니다.')
    click.echo('관리자 생성 완료. 로그인 화면에서 로그인하세요.')


@click.command('backup-db')
@click.argument('destination', type=click.Path(path_type=Path))
@with_appcontext
def backup_db(destination):
    if destination.exists():
        raise click.ClickException('백업 대상이 이미 있습니다. 새 파일 경로를 지정하세요.')
    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(str(destination), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    target = sqlite3.connect(str(destination))
    try:
        get_db().backup(target)
    finally:
        target.close()
    click.echo('일관된 SQLite 백업 생성 완료.')


def init_app(app):
    app.teardown_appcontext(close_db)
    for command in (init_config, init_db, create_admin, backup_db):
        app.cli.add_command(command)
