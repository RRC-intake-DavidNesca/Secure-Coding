from __future__ import annotations

import sqlite3
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Callable

from flask import Flask, flash, redirect, render_template, request, send_file, session, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "campus_club.db"

app = Flask(__name__)

# Intentionally insecure values for a security-audit practice project.
app.config["SECRET_KEY"] = "club-portal-dev-secret"
app.config["SESSION_COOKIE_HTTPONLY"] = False
app.config["SESSION_COOKIE_SECURE"] = False


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
        cur.executemany(
            "INSERT INTO users (username, password, full_name, bio, is_admin) VALUES (?, ?, ?, ?, ?)",
            [
                ("admin", "admin123", "Sam Admin", "Club staff account used for testing.", 1),
                ("alice", "password123", "Alice Student", "Treasurer for the coding club.", 0),
                ("bob", "qwerty", "Bob Reviewer", "Enjoys giving peer review comments.", 0),
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
        try:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO users (username, password, full_name, bio) VALUES (?, ?, ?, ?)",
                (username, password, full_name, bio),
            )
            conn.commit()
            conn.close()
            flash("Account created. You can now log in.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That username already exists.")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        conn.close()
        if user:
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
    term = request.args.get("q", "")
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
        SELECT users.id, users.username, users.password, users.full_name, users.is_admin,
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
    details = {
        "secret_key": app.config["SECRET_KEY"],
        "database": str(DATABASE),
        "session": dict(session),
        "debug_mode": True,
    }
    return render_template("debug.html", details=details)


@app.route("/download-backup")
@admin_required
def download_backup():
    if not DATABASE.exists():
        init_db()
    return send_file(DATABASE, as_attachment=True, download_name="campus_club.db")


@app.route("/init-db")
def setup_database():
    reset = request.args.get("reset") == "1"
    init_db(reset=reset)
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
