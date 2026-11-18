import re
import sqlite3
from functools import wraps

from flask import Blueprint, abort, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import get_db, new_id, now

bp = Blueprint('auth', __name__)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not g.user:
            abort(401)
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if g.user['role'] != 'admin':
            abort(403)
        return view(*args, **kwargs)
    return wrapped


def normalize_email(email):
    email = email.strip().lower()
    if len(email) > 254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email):
        raise ValueError('올바른 이메일 주소를 입력해 주세요.')
    return email


def validate_signup(email, nickname, password):
    email = normalize_email(email)
    nickname = nickname.strip()
    if not 1 <= len(nickname) <= 40:
        raise ValueError('닉네임은 1~40자로 입력해 주세요.')
    if not 6 <= len(password) <= 128 or not password.strip():
        raise ValueError('비밀번호는 6~128자로 입력해 주세요.')
    return email, nickname


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            email, nickname = validate_signup(request.form.get('email', ''), request.form.get('nickname', ''), request.form.get('password', ''))
            db = get_db()
            with db:
                db.execute('INSERT INTO users VALUES (?, ?, ?, ?, ?, ?)',
                           (new_id(), email, nickname, generate_password_hash(request.form['password'], method='pbkdf2:sha256:600000'), 'user', now()))
        except (ValueError, sqlite3.IntegrityError) as error:
            flash(str(error) if isinstance(error, ValueError) else '이미 등록된 이메일입니다.', 'error')
            return render_template('auth.html', mode='signup'), 400
        flash('회원가입이 완료되었습니다. 로그인해 주세요.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth.html', mode='signup')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = get_db().execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        if not user or len(password) > 128 or not check_password_hash(user['password_hash'], password):
            flash('이메일 또는 비밀번호를 확인해 주세요.', 'error')
            return render_template('auth.html', mode='login'), 400
        session.clear()
        session['user_id'] = user['id']
        flash('로그인했습니다.', 'success')
        return redirect(url_for('guestbook.index'))
    return render_template('auth.html', mode='login')


@bp.post('/logout')
def logout():
    session.clear()
    return redirect(url_for('guestbook.index'))


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        try:
            normalize_email(request.form.get('email', ''))
        except ValueError as error:
            flash(str(error), 'error')
            return render_template('auth.html', mode='forgot'), 400
        flash('데모 기능입니다. 이메일을 발송하거나 비밀번호를 변경하지 않습니다.', 'success')
    return render_template('auth.html', mode='forgot')
