from flask import Blueprint, abort, g, jsonify, render_template, request

from .auth import login_required
from .db import get_db, new_id, now
from .masking import masker, preview

bp = Blueprint('guestbook', __name__)
PAGE_SIZE = 10


def listing():
    db = get_db()
    total = db.execute('SELECT count(*) FROM posts').fetchone()[0]
    pages = max(1, (total + PAGE_SIZE - 1) // PAGE_SIZE)
    page = max(1, min(request.args.get('page', 1, type=int), pages))
    rows = db.execute('SELECT p.*, u.nickname FROM posts p JOIN users u ON p.author_id = u.id '
                      'ORDER BY p.created_at DESC, p.id DESC LIMIT ? OFFSET ?',
                      (PAGE_SIZE, (page - 1) * PAGE_SIZE)).fetchall()
    return dict(posts=[dict(id=row['id'], preview=preview(row['body']), nickname=row['nickname'],
                            created_at=row['created_at']) for row in rows],
                page=page, pages=pages, total=total)


def post_or_404(post_id, owner=False):
    row = get_db().execute('SELECT p.*, u.nickname FROM posts p JOIN users u ON p.author_id=u.id WHERE p.id=?', (post_id,)).fetchone()
    if not row:
        abort(404)
    if owner and (not g.user or row['author_id'] != g.user['id']):
        abort(403)
    return row


def input_body(max_length):
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('body'), str):
        abort(400)
    body = data['body'].strip()
    if not body or len(body) > max_length:
        abort(400)
    return body


@bp.get('/')
def index():
    return render_template('index.html', **listing())


@bp.get('/api/posts')
def list_posts():
    return jsonify(listing())


@bp.post('/api/posts')
@login_required
def create_post():
    body = input_body(5000)
    post_id, timestamp = new_id(), now()
    db = get_db()
    with db:
        db.execute('INSERT INTO posts VALUES (?, ?, ?, ?, ?)', (post_id, g.user['id'], body, timestamp, timestamp))
    return jsonify(id=post_id), 201


@bp.get('/api/posts/<post_id>')
def detail(post_id):
    row = post_or_404(post_id)
    comments = get_db().execute('SELECT c.*, u.nickname FROM comments c JOIN users u ON c.author_id=u.id '
                                'WHERE c.post_id=? ORDER BY c.created_at, c.id', (post_id,)).fetchall()
    return jsonify(id=row['id'], body=masker().apply(row['body']), nickname=row['nickname'],
                   created_at=row['created_at'], updated_at=row['updated_at'],
                   is_owner=bool(g.user and g.user['id'] == row['author_id']),
                   comments=[dict(id=c['id'], body=masker().apply(c['body']), nickname=c['nickname'], created_at=c['created_at']) for c in comments])


@bp.get('/api/posts/<post_id>/edit')
@login_required
def edit_source(post_id):
    row = post_or_404(post_id, owner=True)
    return jsonify(body=row['body'])


@bp.patch('/api/posts/<post_id>')
@login_required
def update_post(post_id):
    post_or_404(post_id, owner=True)
    body = input_body(5000)
    db = get_db()
    with db:
        db.execute('UPDATE posts SET body=?, updated_at=? WHERE id=? AND author_id=?', (body, now(), post_id, g.user['id']))
    return jsonify(ok=True)


@bp.delete('/api/posts/<post_id>')
@login_required
def delete_post(post_id):
    post_or_404(post_id, owner=True)
    db = get_db()
    with db:
        db.execute('DELETE FROM posts WHERE id=? AND author_id=?', (post_id, g.user['id']))
    return jsonify(ok=True)


@bp.post('/api/posts/<post_id>/comments')
@login_required
def create_comment(post_id):
    post_or_404(post_id)
    body = input_body(1000)
    db = get_db()
    with db:
        db.execute('INSERT INTO comments VALUES (?, ?, ?, ?, ?)', (new_id(), post_id, g.user['id'], body, now()))
    return jsonify(ok=True), 201
