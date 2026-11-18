BEGIN;
CREATE TABLE users (
    id TEXT PRIMARY KEY NOT NULL,
    email TEXT NOT NULL UNIQUE,
    nickname TEXT NOT NULL CHECK(length(trim(nickname)) BETWEEN 1 AND 40),
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user' CHECK(role IN ('user', 'admin')),
    created_at TEXT NOT NULL
);
CREATE TABLE posts (
    id TEXT PRIMARY KEY NOT NULL,
    author_id TEXT NOT NULL REFERENCES users(id),
    body TEXT NOT NULL CHECK(length(trim(body)) BETWEEN 1 AND 5000),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE comments (
    id TEXT PRIMARY KEY NOT NULL,
    post_id TEXT NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
    author_id TEXT NOT NULL REFERENCES users(id),
    body TEXT NOT NULL CHECK(length(trim(body)) BETWEEN 1 AND 1000),
    created_at TEXT NOT NULL
);
CREATE TABLE masking_rules (
    id TEXT PRIMARY KEY NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('keyword', 'regex')),
    pattern TEXT NOT NULL CHECK(length(trim(pattern)) BETWEEN 1 AND 200),
    flags TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    UNIQUE(type, pattern, flags),
    CHECK(type = 'regex' OR flags = '')
);
CREATE INDEX posts_created ON posts(created_at DESC, id DESC);
CREATE INDEX comments_post_created ON comments(post_id, created_at, id);
PRAGMA user_version = 1;
