import sqlite3
from datetime import datetime

from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)
app.config.setdefault("DATABASE", "board.db")


def get_connection():
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


@app.route("/")
def list_posts():
    conn = get_connection()
    posts = conn.execute(
        "SELECT id, title, content, created_at FROM posts ORDER BY id DESC"
    ).fetchall()
    conn.close()

    view = request.args.get("view", "sidebar")
    if view not in {"sidebar", "center", "split"}:
        view = "sidebar"

    return render_template("list.html", posts=posts, view=view)


@app.route("/posts/<int:post_id>")
def show_post(post_id: int):
    conn = get_connection()
    post = conn.execute(
        "SELECT id, title, content, created_at FROM posts WHERE id = ?",
        (post_id,),
    ).fetchone()
    conn.close()

    if post is None:
        abort(404)

    view = request.args.get("view", "sidebar")
    if view not in {"sidebar", "center", "split"}:
        view = "sidebar"

    return render_template("detail.html", post=post, view=view)


@app.route("/posts/<int:post_id>/edit", methods=["GET", "POST"])
def edit_post(post_id: int):
    conn = get_connection()
    post = conn.execute(
        "SELECT id, title, content, created_at FROM posts WHERE id = ?",
        (post_id,),
    ).fetchone()

    if post is None:
        conn.close()
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            conn.close()
            return render_template(
                "write.html",
                error="제목과 본문을 입력해주세요",
                title=title,
                content=content,
                form_action=url_for("edit_post", post_id=post_id),
                form_title="글 수정",
            )

        conn.execute(
            "UPDATE posts SET title = ?, content = ? WHERE id = ?",
            (title, content, post_id),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("show_post", post_id=post_id))

    conn.close()
    return render_template(
        "write.html",
        error=None,
        title=post["title"],
        content=post["content"],
        form_action=url_for("edit_post", post_id=post_id),
        form_title="글 수정",
    )


@app.route("/posts/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id: int):
    conn = get_connection()
    conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("list_posts"))


@app.route("/write", methods=["GET", "POST"])
def write_post():
    error = None

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()

        if not title or not content:
            error = "제목과 본문을 입력해주세요"
            return render_template("write.html", error=error, title=title, content=content)

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_connection()
        conn.execute(
            "INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)",
            (title, content, created_at),
        )
        post_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        conn.close()

        return redirect(url_for("show_post", post_id=post_id))

    return render_template("write.html", error=error, title="", content="")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
