import sqlite3

from flask import Blueprint, jsonify, render_template, request

from .auth import admin_required
from .db import get_db, new_id, now
from .masking import MAX_RULES, validate_rule

bp = Blueprint('admin', __name__)


@bp.get('/admin')
@admin_required
def index():
    return render_template('admin.html', rules=get_db().execute('SELECT * FROM masking_rules ORDER BY created_at DESC, id').fetchall())


@bp.post('/api/rules')
@admin_required
def add_rule():
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or any(not isinstance(data.get(key, ''), str) for key in ('type', 'pattern', 'flags')):
        return jsonify(error='규칙 입력값을 확인해 주세요.'), 400
    try:
        values = validate_rule(data.get('type', ''), data.get('pattern', ''), data.get('flags', ''))
        db = get_db()
        with db:
            db.execute('BEGIN IMMEDIATE')
            if db.execute('SELECT count(*) FROM masking_rules').fetchone()[0] >= MAX_RULES:
                return jsonify(error='규칙은 최대 200개까지 등록할 수 있습니다.'), 400
            db.execute('INSERT INTO masking_rules VALUES (?, ?, ?, ?, ?)', (new_id(), *values, now()))
    except ValueError as error:
        return jsonify(error=str(error)), 400
    except sqlite3.IntegrityError:
        return jsonify(error='이미 등록된 규칙입니다.'), 409
    return jsonify(ok=True), 201


@bp.delete('/api/rules/<rule_id>')
@admin_required
def delete_rule(rule_id):
    db = get_db()
    with db:
        result = db.execute('DELETE FROM masking_rules WHERE id=?', (rule_id,))
    return (jsonify(ok=True), 200) if result.rowcount else (jsonify(error='규칙을 찾을 수 없습니다.'), 404)
