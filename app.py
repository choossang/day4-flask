import os
import sqlite3
import uuid
from datetime import datetime
import html as html_mod
import re

import requests as http_requests
from bs4 import BeautifulSoup
from flask import Flask, abort, redirect, render_template, request, url_for

app = Flask(__name__)
app.config.setdefault("DATABASE", "board.db")

UPLOAD_FOLDER = os.path.join(app.static_folder, "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def save_upload(file):
    if file and file.filename and allowed_file(file.filename):
        ext = file.filename.rsplit(".", 1)[1].lower()
        filename = f"{uuid.uuid4().hex[:12]}.{ext}"
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return url_for("static", filename=f"uploads/{filename}")
    return ""


def init_db_if_needed():
    conn = get_connection()
    table_exists = conn.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'posts'"
    ).fetchone()
    if table_exists is None:
        conn.execute(
            """
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT '',
                image_url TEXT NOT NULL DEFAULT ''
            )
            """
        )
        conn.commit()
    conn.close()


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
            created_at TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT '',
            image_url TEXT NOT NULL DEFAULT ''
        )
        """
    )
    conn.commit()
    conn.close()


@app.before_request
def ensure_schema():
    init_db_if_needed()


PER_PAGE = 10
CATEGORIES = [
    "인사·만남", "카페·식당", "교통·이동", "쇼핑", "병원·건강",
    "금융·업무", "일상대화", "숙박·여행", "직장·비즈니스", "학교·교육",
    "관광·여가", "일상생활", "공항·여행", "긴급상황",
]
SORT_OPTIONS = {"latest": "id DESC", "oldest": "id ASC", "title": "title ASC"}


@app.route("/")
def list_posts():
    page = request.args.get("page", 1, type=int)
    view = request.args.get("view", "sidebar")
    if view not in {"sidebar", "center", "split"}:
        view = "sidebar"
    query = request.args.get("q", "").strip()
    sort = request.args.get("sort", "latest")
    if sort not in SORT_OPTIONS:
        sort = "latest"
    order_by = SORT_OPTIONS[sort]

    conn = get_connection()
    if query:
        like = f"%{query}%"
        total = conn.execute(
            "SELECT COUNT(*) FROM posts WHERE title LIKE ? OR content LIKE ?",
            (like, like),
        ).fetchone()[0]
        posts = conn.execute(
            f"SELECT * FROM posts WHERE title LIKE ? OR content LIKE ? ORDER BY {order_by} LIMIT ? OFFSET ?",
            (like, like, PER_PAGE, (page - 1) * PER_PAGE),
        ).fetchall()
    else:
        total = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        posts = conn.execute(
            f"SELECT * FROM posts ORDER BY {order_by} LIMIT ? OFFSET ?",
            (PER_PAGE, (page - 1) * PER_PAGE),
        ).fetchall()
    conn.close()

    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)

    return render_template(
        "list.html",
        posts=posts,
        view=view,
        page=page,
        total_pages=total_pages,
        query=query,
        sort=sort,
    )


@app.route("/posts/<int:post_id>")
def show_post(post_id: int):
    conn = get_connection()
    post = conn.execute(
        "SELECT * FROM posts WHERE id = ?",
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
        "SELECT * FROM posts WHERE id = ?",
        (post_id,),
    ).fetchone()

    if post is None:
        conn.close()
        abort(404)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        category = request.form.get("category", "").strip()
        image_url = post["image_url"]

        if not title or not content:
            conn.close()
            return render_template(
                "write.html",
                error="제목과 본문을 입력해주세요",
                title=title,
                content=content,
                category=category,
                image_url=image_url,
                form_action=url_for("edit_post", post_id=post_id),
                form_title="글 수정",
                categories=CATEGORIES,
            )

        file = request.files.get("image")
        if file and file.filename:
            uploaded = save_upload(file)
            if uploaded:
                image_url = uploaded

        conn.execute(
            "UPDATE posts SET title = ?, content = ?, category = ?, image_url = ? WHERE id = ?",
            (title, content, category, image_url, post_id),
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
        category=post["category"],
        image_url=post["image_url"],
        form_action=url_for("edit_post", post_id=post_id),
        form_title="글 수정",
        categories=CATEGORIES,
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
        category = request.form.get("category", "").strip()
        image_url = ""

        if not title or not content:
            error = "제목과 본문을 입력해주세요"
            return render_template(
                "write.html",
                error=error,
                title=title,
                content=content,
                category=category,
                image_url=image_url,
                categories=CATEGORIES,
            )

        file = request.files.get("image")
        if file and file.filename:
            uploaded = save_upload(file)
            if uploaded:
                image_url = uploaded

        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = get_connection()
        conn.execute(
            "INSERT INTO posts (title, content, created_at, category, image_url) VALUES (?, ?, ?, ?, ?)",
            (title, content, created_at, category, image_url),
        )
        post_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        conn.commit()
        conn.close()

        return redirect(url_for("show_post", post_id=post_id))

    return render_template(
        "write.html",
        error=error,
        title="",
        content="",
        category="",
        image_url="",
        categories=CATEGORIES,
    )


@app.route("/news")
def news():
    url = "https://news.google.com/rss?hl=ko&gl=KR&ceid=KR:ko"
    try:
        resp = http_requests.get(url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "xml")
    except Exception:
        return render_template("news.html", items=[], error="뉴스를 가져오지 못했습니다.")

    items = []
    for item in soup.find_all("item")[:10]:
        pub_date = item.find("pubDate")
        pub_date_text = pub_date.get_text(strip=True) if pub_date else ""
        try:
            dt = datetime.strptime(pub_date_text, "%a, %d %b %Y %H:%M:%S GMT")
            pub_date_text = dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            pass

        desc_raw = item.find("description").get_text(strip=True) if item.find("description") else ""
        desc_clean = html_mod.unescape(re.sub(r"<[^>]+>", "", desc_raw)).replace("\xa0", " ")

        items.append({
            "title": item.find("title").get_text(strip=True) if item.find("title") else "",
            "link": item.find("link").get_text(strip=True) if item.find("link") else "",
            "description": desc_clean[:120],
            "pub_date": pub_date_text,
        })

    for i, it in enumerate(items, 1):
        print(f"[{i}] {it['title']}")
        print(f"    {it['pub_date']}")
        print(f"    {it['link']}")
        print(f"    {it['description'][:80]}...")
        print()

    return render_template("news.html", items=items, error=None)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
