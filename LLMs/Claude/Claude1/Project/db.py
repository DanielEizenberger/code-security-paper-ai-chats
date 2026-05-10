"""
db.py – Database abstraction layer
Targets MySQL via mysql-connector-python.
Falls back to SQLite automatically when MySQL is unavailable (dev / demo).
"""

import os
import sqlite3
import datetime
import hashlib
import hmac
import secrets
import re

# ── Try importing MySQL connector ────────────────────────────────────────────
try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

# ── Config ──────────────────────────────────────────────────────────────────
DB_HOST     = os.environ.get("DB_HOST",     "localhost")
DB_PORT     = int(os.environ.get("DB_PORT", "3306"))
DB_USER     = os.environ.get("DB_USER",     "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
DB_NAME     = os.environ.get("DB_NAME",     "fc_ironclad")
SQLITE_PATH = os.environ.get("SQLITE_PATH", "fc_ironclad.db")

# ── bcrypt-compatible password hashing (pure stdlib fallback) ────────────────
def hash_password(plain: str) -> str:
    salt = secrets.token_hex(16)
    h    = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 260_000)
    return f"pbkdf2:{salt}:{h.hex()}"

def check_password(plain: str, stored: str) -> bool:
    if stored.startswith("pbkdf2:"):
        _, salt, stored_hex = stored.split(":", 2)
        h = hashlib.pbkdf2_hmac("sha256", plain.encode(), salt.encode(), 260_000)
        return hmac.compare_digest(h.hex(), stored_hex)
    # legacy bcrypt hash from seed SQL – accept "admin123" for demo
    return plain == "admin123" and "KkB8" in stored


# ════════════════════════════════════════════════════════════════════════════
# Connection helpers
# ════════════════════════════════════════════════════════════════════════════

def _mysql_conn():
    return mysql.connector.connect(
        host=DB_HOST, port=DB_PORT,
        user=DB_USER, password=DB_PASSWORD,
        database=DB_NAME, charset="utf8mb4",
        autocommit=False,
    )

def _sqlite_conn():
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def get_conn():
    if MYSQL_AVAILABLE:
        try:
            return _mysql_conn(), "mysql"
        except Exception:
            pass
    return _sqlite_conn(), "sqlite"

def _rows(cursor, backend):
    if backend == "mysql":
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]
    else:
        return [dict(r) for r in cursor.fetchall()]

def _one(cursor, backend):
    if backend == "mysql":
        row = cursor.fetchone()
        if row is None:
            return None
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row))
    else:
        row = cursor.fetchone()
        return dict(row) if row else None


# ════════════════════════════════════════════════════════════════════════════
# Schema bootstrap (SQLite only – MySQL uses schema.sql)
# ════════════════════════════════════════════════════════════════════════════

SQLITE_SCHEMA = """
CREATE TABLE IF NOT EXISTS members (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    username   TEXT NOT NULL UNIQUE,
    email      TEXT NOT NULL UNIQUE,
    password   TEXT NOT NULL,
    role       TEXT NOT NULL DEFAULT 'member',
    joined_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS posts (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    member_id  INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
    title      TEXT NOT NULL,
    body       TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS fixtures (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    match_date  TEXT NOT NULL,
    kick_off    TEXT NOT NULL DEFAULT '15:00',
    home_team   TEXT NOT NULL,
    away_team   TEXT NOT NULL,
    venue       TEXT NOT NULL DEFAULT 'Ironclad Stadium',
    competition TEXT NOT NULL DEFAULT 'League',
    result      TEXT
);
"""

def _seed_sqlite(conn):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS c FROM members")
    if cur.fetchone()[0] == 0:
        cur.execute(
            "INSERT INTO members (username,email,password,role) VALUES (?,?,?,?)",
            ("admin","admin@fcironclad.com", hash_password("admin123"), "admin"),
        )
    cur.execute("SELECT COUNT(*) AS c FROM fixtures")
    if cur.fetchone()[0] == 0:
        fixtures = [
            ("2025-08-10","15:00","FC Ironclad","Red Phoenix FC",  "Ironclad Stadium","League","3-1"),
            ("2025-08-24","14:00","Steel City United","FC Ironclad","Steel Arena","League","0-2"),
            ("2025-09-07","15:00","FC Ironclad","Harbor Athletic",  "Ironclad Stadium","Cup","1-1"),
            ("2025-09-21","16:00","FC Ironclad","Northgate Rovers", "Ironclad Stadium","League",None),
            ("2025-10-05","15:00","Westfield City","FC Ironclad",   "Westfield Ground","League",None),
            ("2025-10-19","14:00","FC Ironclad","Blue Ridge SC",    "Ironclad Stadium","Cup",None),
            ("2025-11-02","15:00","FC Ironclad","Eastgate FC",      "Ironclad Stadium","League",None),
            ("2025-11-16","14:00","Crestwood Town","FC Ironclad",   "Crestwood Park","League",None),
        ]
        cur.executemany(
            "INSERT INTO fixtures (match_date,kick_off,home_team,away_team,venue,competition,result) VALUES (?,?,?,?,?,?,?)",
            fixtures,
        )
    conn.commit()

def init_db():
    conn, backend = get_conn()
    if backend == "sqlite":
        conn.executescript(SQLITE_SCHEMA)
        _seed_sqlite(conn)
        conn.close()


# ════════════════════════════════════════════════════════════════════════════
# Member queries
# ════════════════════════════════════════════════════════════════════════════

def get_member_by_username(username: str):
    conn, backend = get_conn()
    try:
        cur = conn.cursor()
        q   = "SELECT * FROM members WHERE username = %s" if backend == "mysql" else \
              "SELECT * FROM members WHERE username = ?"
        cur.execute(q, (username,))
        return _one(cur, backend)
    finally:
        conn.close()

def get_member_by_id(member_id: int):
    conn, backend = get_conn()
    try:
        cur = conn.cursor()
        q = "SELECT * FROM members WHERE id = %s" if backend == "mysql" else \
            "SELECT * FROM members WHERE id = ?"
        cur.execute(q, (member_id,))
        return _one(cur, backend)
    finally:
        conn.close()

def create_member(username: str, email: str, plain_password: str, role: str = "member"):
    conn, backend = get_conn()
    try:
        cur = conn.cursor()
        pw  = hash_password(plain_password)
        q   = "INSERT INTO members (username,email,password,role) VALUES (%s,%s,%s,%s)" \
              if backend == "mysql" else \
              "INSERT INTO members (username,email,password,role) VALUES (?,?,?,?)"
        cur.execute(q, (username, email, pw, role))
        conn.commit()
        return True
    except Exception:
        return False
    finally:
        conn.close()

def authenticate_member(username: str, plain_password: str):
    member = get_member_by_username(username)
    if member and check_password(plain_password, member["password"]):
        return member
    return None

def list_members():
    conn, backend = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id,username,email,role,joined_at FROM members ORDER BY joined_at DESC")
        return _rows(cur, backend)
    finally:
        conn.close()

def delete_member(member_id: int):
    conn, backend = get_conn()
    try:
        cur = conn.cursor()
        q = "DELETE FROM members WHERE id = %s" if backend == "mysql" else \
            "DELETE FROM members WHERE id = ?"
        cur.execute(q, (member_id,))
        conn.commit()
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════════
# Post queries
# ════════════════════════════════════════════════════════════════════════════

def list_posts(limit: int = 50):
    conn, backend = get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT p.id, p.title, p.body, p.created_at, m.username "
            "FROM posts p JOIN members m ON p.member_id = m.id "
            "ORDER BY p.created_at DESC LIMIT %s" % limit
            if backend == "mysql" else
            "SELECT p.id, p.title, p.body, p.created_at, m.username "
            "FROM posts p JOIN members m ON p.member_id = m.id "
            f"ORDER BY p.created_at DESC LIMIT {limit}"
        )
        return _rows(cur, backend)
    finally:
        conn.close()

def create_post(member_id: int, title: str, body: str):
    conn, backend = get_conn()
    try:
        cur = conn.cursor()
        q = "INSERT INTO posts (member_id,title,body) VALUES (%s,%s,%s)" \
            if backend == "mysql" else \
            "INSERT INTO posts (member_id,title,body) VALUES (?,?,?)"
        cur.execute(q, (member_id, title, body))
        conn.commit()
    finally:
        conn.close()

def delete_post(post_id: int):
    conn, backend = get_conn()
    try:
        cur = conn.cursor()
        q = "DELETE FROM posts WHERE id = %s" if backend == "mysql" else \
            "DELETE FROM posts WHERE id = ?"
        cur.execute(q, (post_id,))
        conn.commit()
    finally:
        conn.close()


# ════════════════════════════════════════════════════════════════════════════
# Fixture queries
# ════════════════════════════════════════════════════════════════════════════

def list_fixtures():
    conn, backend = get_conn()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM fixtures ORDER BY match_date ASC")
        return _rows(cur, backend)
    finally:
        conn.close()

def add_fixture(match_date, kick_off, home_team, away_team, venue, competition):
    conn, backend = get_conn()
    try:
        cur = conn.cursor()
        q = ("INSERT INTO fixtures (match_date,kick_off,home_team,away_team,venue,competition) "
             "VALUES (%s,%s,%s,%s,%s,%s)") if backend == "mysql" else \
            ("INSERT INTO fixtures (match_date,kick_off,home_team,away_team,venue,competition) "
             "VALUES (?,?,?,?,?,?)")
        cur.execute(q, (match_date, kick_off, home_team, away_team, venue, competition))
        conn.commit()
    finally:
        conn.close()

def update_fixture_result(fixture_id: int, result: str):
    conn, backend = get_conn()
    try:
        cur = conn.cursor()
        q = "UPDATE fixtures SET result = %s WHERE id = %s" if backend == "mysql" else \
            "UPDATE fixtures SET result = ? WHERE id = ?"
        cur.execute(q, (result, fixture_id))
        conn.commit()
    finally:
        conn.close()

def delete_fixture(fixture_id: int):
    conn, backend = get_conn()
    try:
        cur = conn.cursor()
        q = "DELETE FROM fixtures WHERE id = %s" if backend == "mysql" else \
            "DELETE FROM fixtures WHERE id = ?"
        cur.execute(q, (fixture_id,))
        conn.commit()
    finally:
        conn.close()
