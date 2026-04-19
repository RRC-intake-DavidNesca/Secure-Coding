from __future__ import annotations

import os
import secrets
import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "campus_club.db"

MAX_USERNAME_LEN = 80
MIN_USERNAME_LEN = 2
MAX_PASSWORD_LEN = 200
MIN_PASSWORD_LEN = 8
MAX_FULL_NAME_LEN = 120
MAX_BIO_LEN = 2000
MAX_POST_TITLE_LEN = 200
MAX_POST_BODY_LEN = 20000
MAX_NOTE_TITLE_LEN = 200
MAX_NOTE_BODY_LEN = 20000
MAX_SEARCH_LEN = 200

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = os.environ.get("SESSION_COOKIE_SECURE", "").lower() in (
    "1",
    "true",
    "yes",
)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["WTF_CSRF_TIME_LIMIT"] = None

csrf = CSRFProtect(app)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=[],
    storage_uri="memory://",
)


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any):
        if "user_id" not in session:
            flash("Please log in first.")
            return redirect(url_for("login"))
        if not session.get("is_admin"):
            flash("You do not have permission to view this page.")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)

    return wrapped


def validate_registration(username: str, password: str, full_name: str, bio: str) -> str | None:
    u = username.strip()
    if len(u) < MIN_USERNAME_LEN or len(u) > MAX_USERNAME_LEN:
        return f"Username must be between {MIN_USERNAME_LEN} and {MAX_USERNAME_LEN} characters."
    if len(password) < MIN_PASSWORD_LEN or len(password) > MAX_PASSWORD_LEN:
        return f"Password must be between {MIN_PASSWORD_LEN} and {MAX_PASSWORD_LEN} characters."
    fn = full_name.strip()
    if not fn or len(fn) > MAX_FULL_NAME_LEN:
        return "Full name is required and must not exceed the maximum length."
    if len(bio.strip()) > MAX_BIO_LEN:
        return "Bio is too long."
    return None


def validate_login_fields(username: str, password: str) -> str | None:
    if not username.strip() or not password:
        return "Username and password are required."
    if len(username) > MAX_USERNAME_LEN or len(password) > MAX_PASSWORD_LEN:
        return "Invalid login."
    return None


def validate_post_fields(title: str, content: str) -> str | None:
    t = title.strip()
    c = content.strip()
    if not t or not c:
        return "Title and content are required."
    if len(t) > MAX_POST_TITLE_LEN or len(c) > MAX_POST_BODY_LEN:
        return "Post title or content is too long."
    return None


def validate_note_fields(title: str, body: str) -> str | None:
    t = title.strip()
    b = body.strip()
    if not t or not b:
        return "Note title and body are required."
    if len(t) > MAX_NOTE_TITLE_LEN or len(b) > MAX_NOTE_BODY_LEN:
        return "Note title or body is too long."
    return None


def init_db(reset: bool = False) -> None:
    if reset and DATABASE.exists():
        DATABASE.unlink()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            bio TEXT DEFAULT '',
            is_admin INTEGER DEFAULT 0
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.commit()

    user_count = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if user_count == 0:
        seed_users = [
            ("admin", "admin123", "Sam Admin", "Club staff account used for testing.", 1),
            ("alice", "password123", "Alice Student", "Treasurer for the coding club.", 0),
            ("bob", "qwerty", "Bob Reviewer", "Enjoys giving peer review comments.", 0),
        ]
        cur.executemany(
            "INSERT INTO users (username, password, full_name, bio, is_admin) VALUES (?, ?, ?, ?, ?)",
            [
                (u, generate_password_hash(p), fn, bio, adm)
                for (u, p, fn, bio, adm) in seed_users
            ],
        )
        cur.executemany(
            "INSERT INTO posts (owner_id, title, content, created_at) VALUES (?, ?, ?, ?)",
            [
                (2, "Welcome Meeting", "Bring your laptop and ideas for this term's projects.", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                (3, "Code Review Volunteers", "We need two volunteers to review pull requests this week.", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ],
        )
        cur.executemany(
            "INSERT INTO notes (owner_id, title, body, created_at) VALUES (?, ?, ?, ?)",
            [
                (2, "Budget draft", "Treasurer notes: ask instructor before buying anything.", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                (3, "Review checklist", "Check auth, input validation, SQL queries, and session handling.", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            ],
        )

    conn.commit()
    conn.close()


@app.context_processor
def inject_user() -> dict[str, object]:
    return {
        "current_user": session.get("username"),
        "current_user_id": session.get("user_id"),
        "current_user_is_admin": bool(session.get("is_admin")),
    }


@app.route("/")
def index():
    conn = get_db_connection()
    posts = conn.execute(
        """
        SELECT posts.id, posts.title, posts.content, posts.created_at, users.username
        FROM posts
        JOIN users ON users.id = posts.owner_id
        ORDER BY posts.id DESC
        """
    ).fetchall()
    conn.close()
    return render_template("index.html", posts=posts)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        full_name = request.form.get("full_name", "")
        bio = request.form.get("bio", "")
        reg_err = validate_registration(username, password, full_name, bio)
        if reg_err:
            flash(reg_err)
            return render_template("register.html")
        username = username.strip()
        full_name = full_name.strip()
        bio = bio.strip()
        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (username, password, full_name, bio) VALUES (?, ?, ?, ?)",
                (username, generate_password_hash(password), full_name, bio),
            )
            conn.commit()
            conn.close()
            flash("Account created. You can now log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That username already exists.")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per minute", exempt_when=lambda: request.method != "POST")
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        login_err = validate_login_fields(username, password)
        if login_err:
            flash(login_err)
            return render_template("login.html")
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["is_admin"] = bool(user["is_admin"])
            flash("Logged in successfully.")
            return redirect(url_for("dashboard"))
        flash("Login failed.")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("index"))


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "user_id" not in session:
        flash("Please log in first.")
        return redirect(url_for("login"))
    if request.method == "POST":
        title = request.form.get("title", "")
        body = request.form.get("body", "")
        note_err = validate_note_fields(title, body)
        if note_err:
            flash(note_err)
            return redirect(url_for("dashboard"))
        title = title.strip()
        body = body.strip()
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO notes (owner_id, title, body, created_at) VALUES (?, ?, ?, ?)",
            (session["user_id"], title, body, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.commit()
        conn.close()
        flash("Private note saved.")
        return redirect(url_for("dashboard"))
    conn = get_db_connection()
    notes = conn.execute("SELECT * FROM notes WHERE owner_id = ? ORDER BY id DESC", (session["user_id"],)).fetchall()
    conn.close()
    return render_template("dashboard.html", notes=notes)


@app.route("/post", methods=["POST"])
def create_post():
    if "user_id" not in session:
        flash("Please log in to post.")
        return redirect(url_for("login"))
    title = request.form.get("title", "")
    content = request.form.get("content", "")
    post_err = validate_post_fields(title, content)
    if post_err:
        flash(post_err)
        return redirect(url_for("index"))
    title = title.strip()
    content = content.strip()
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO posts (owner_id, title, content, created_at) VALUES (?, ?, ?, ?)",
        (session["user_id"], title, content, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    )
    conn.commit()
    conn.close()
    flash("Post added.")
    return redirect(url_for("index"))


@app.route("/notes/<int:user_id>")
@login_required
def user_notes(user_id: int):
    viewer_id = session["user_id"]
    if viewer_id != user_id and not session.get("is_admin"):
        flash("You can only open your own private notes.")
        return redirect(url_for("dashboard"))
    conn = get_db_connection()
    owner = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not owner:
        conn.close()
        flash("User not found.")
        return redirect(url_for("dashboard"))
    notes = conn.execute("SELECT * FROM notes WHERE owner_id = ? ORDER BY id DESC", (user_id,)).fetchall()
    conn.close()
    return render_template("notes.html", owner=owner, notes=notes)


@app.route("/search")
def search():
    term = request.args.get("q", "")[:MAX_SEARCH_LEN]
    results = []
    if term:
        conn = get_db_connection()
        like = f"%{term}%"
        results = conn.execute(
            "SELECT posts.id, posts.title, posts.content, users.username "
            "FROM posts JOIN users ON users.id = posts.owner_id "
            "WHERE posts.title LIKE ? OR posts.content LIKE ?",
            (like, like),
        ).fetchall()
        conn.close()
    return render_template("search.html", results=results, term=term)


@app.route("/admin")
@admin_required
def admin():
    conn = get_db_connection()
    users = conn.execute(
        """
        SELECT users.id, users.username, users.full_name, users.is_admin,
               COUNT(notes.id) AS note_count
        FROM users
        LEFT JOIN notes ON notes.owner_id = users.id
        GROUP BY users.id
        ORDER BY users.id
        """
    ).fetchall()
    conn.close()
    return render_template("admin.html", users=users)


@app.route("/debug-info")
@admin_required
def debug_info():
    if os.environ.get("SECRET_KEY"):
        secret_desc = "Loaded from SECRET_KEY environment variable."
    else:
        secret_desc = "Generated for this process; set SECRET_KEY for a stable value across restarts."
    details = {
        "secret_key": secret_desc,
        "database": str(DATABASE),
        "session": dict(session),
        "debug_mode": app.debug,
    }
    return render_template("debug.html", details=details)


@app.route("/download-backup")
@admin_required
def download_backup():
    if not DATABASE.exists():
        init_db()
    return send_file(DATABASE, as_attachment=True, download_name="campus_club.db")


@app.get("/init-db")
def init_db_legacy_notice():
    flash("Database tools are on the Admin page (administrators only).")
    return redirect(url_for("index"))


@app.post("/init-db")
@admin_required
def setup_database():
    reset = request.form.get("reset") == "1"
    init_db(reset=reset)
    if reset:
        flash("Database was reset and re-seeded.")
    else:
        flash("Database schema was ensured.")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    init_db()
    _debug = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes")
    _host = os.environ.get("FLASK_RUN_HOST", "127.0.0.1")
    _port = int(os.environ.get("FLASK_RUN_PORT", "5000"))
    app.run(debug=_debug, host=_host, port=_port)
