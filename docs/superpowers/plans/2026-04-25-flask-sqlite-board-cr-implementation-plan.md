# Flask + SQLite 게시판 C/R Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 제공된 3개 디자인 무드를 혼합한 Flask + SQLite 게시판에서 글쓰기(C), 목록(R), 상세(R) 기능을 완성한다.

**Architecture:** `app.py` 단일 백엔드 파일에서 SQLite 연결/쿼리/라우팅을 담당하고, Jinja 템플릿(`base/list/detail/write`)으로 화면을 분리한다. 공통 스타일은 `static/style.css`로 관리해 beige/minimal 톤을 통일한다. 데이터는 `board.db`의 `posts(id, title, content, created_at)` 한 테이블만 사용한다.

**Tech Stack:** Python 3, Flask, SQLite3, Jinja2, pytest

---

## File Structure Map

- `app.py` (modify): Flask 앱, DB 초기화, 조회/삽입 함수, `/`, `/posts/<id>`, `/write` 라우트
- `templates/base.html` (create): 공통 레이아웃, 상단 네비, CSS 링크, 컨테이너
- `templates/list.html` (create): 목록 화면, 빈 상태 UI, 게시글 카드
- `templates/detail.html` (create): 상세 화면, 제목/날짜/본문
- `templates/write.html` (create): 글쓰기 폼, 에러 메시지
- `static/style.css` (create): 베이지 톤, 타이포, 버튼/카드/폼 스타일
- `tests/test_board.py` (create/modify): 라우트/검증/저장/404 동작 테스트

---

### Task 1: 프로젝트 기본 뼈대 + 목록/빈 상태 구현

**Files:**
- Modify: `app.py`
- Create: `templates/base.html`
- Create: `templates/list.html`
- Create: `tests/test_board.py`

- [ ] **Step 1: Write the failing test (empty state)**

```python
# tests/test_board.py
import sqlite3
import pytest

from app import app, init_db


@pytest.fixture
def client(tmp_path):
    test_db = tmp_path / "test.db"
    app.config.update(TESTING=True, DATABASE=str(test_db))
    init_db()
    with app.test_client() as test_client:
        yield test_client


def test_list_page_shows_empty_state_when_no_posts(client):
    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "아직 게시글이 없습니다" in html
    assert "글쓰기" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_board.py::test_list_page_shows_empty_state_when_no_posts -v`
Expected: FAIL (현재 `app.py`는 Hello World만 반환)

- [ ] **Step 3: Write minimal implementation for list/empty state**

```python
# app.py
import sqlite3
from flask import Flask, render_template

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
    return render_template("list.html", posts=posts)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
```

```html
<!-- templates/base.html -->
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{% block title %}Warm Board{% endblock %}</title>
  </head>
  <body>
    <header>
      <nav>
        <a href="{{ url_for('list_posts') }}">목록</a>
        <a href="{{ url_for('write_post') }}">글쓰기</a>
      </nav>
    </header>
    <main>{% block content %}{% endblock %}</main>
  </body>
</html>
```

```html
<!-- templates/list.html -->
{% extends "base.html" %}
{% block title %}게시글 목록{% endblock %}
{% block content %}
  <h1>게시글 목록</h1>

  {% if posts %}
    <ul>
      {% for post in posts %}
        <li>
          <a href="{{ url_for('show_post', post_id=post['id']) }}">{{ post['title'] }}</a>
        </li>
      {% endfor %}
    </ul>
  {% else %}
    <p>아직 게시글이 없습니다</p>
    <a href="{{ url_for('write_post') }}">글쓰기</a>
  {% endif %}
{% endblock %}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_board.py::test_list_page_shows_empty_state_when_no_posts -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git rev-parse --is-inside-work-tree || git init
git add app.py templates/base.html templates/list.html tests/test_board.py
git commit -m "feat: add list page with sqlite setup and empty state"
```

---

### Task 2: 상세 보기(R) 구현 + 404 처리

**Files:**
- Modify: `app.py`
- Modify: `tests/test_board.py`
- Create: `templates/detail.html`

- [ ] **Step 1: Write failing tests for detail page and 404**

```python
# tests/test_board.py 에 아래 코드 추가

def insert_post_for_test(title: str, content: str, created_at: str):
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.execute(
        "INSERT INTO posts (title, content, created_at) VALUES (?, ?, ?)",
        (title, content, created_at),
    )
    post_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
    conn.commit()
    conn.close()
    return post_id


def test_detail_page_renders_saved_post(client):
    post_id = insert_post_for_test("첫 글", "본문입니다", "2026-04-25 10:00:00")

    response = client.get(f"/posts/{post_id}")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "첫 글" in html
    assert "본문입니다" in html
    assert "2026-04-25 10:00:00" in html


def test_detail_page_returns_404_for_missing_post(client):
    response = client.get("/posts/99999")
    assert response.status_code == 404
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_board.py::test_detail_page_renders_saved_post tests/test_board.py::test_detail_page_returns_404_for_missing_post -v`
Expected: FAIL (`/posts/<id>` 라우트 미구현)

- [ ] **Step 3: Implement minimal detail route and template**

```python
# app.py 에 추가/수정
from flask import Flask, render_template, abort


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

    return render_template("detail.html", post=post)
```

```html
<!-- templates/detail.html -->
{% extends "base.html" %}
{% block title %}{{ post['title'] }}{% endblock %}
{% block content %}
  <article>
    <h1>{{ post['title'] }}</h1>
    <p>{{ post['created_at'] }}</p>
    <div>{{ post['content'] }}</div>
    <p><a href="{{ url_for('list_posts') }}">목록으로</a></p>
  </article>
{% endblock %}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_board.py::test_detail_page_renders_saved_post tests/test_board.py::test_detail_page_returns_404_for_missing_post -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app.py templates/detail.html tests/test_board.py
git commit -m "feat: add post detail route with 404 handling"
```

---

### Task 3: 글쓰기(C) 구현 + 서버 검증 + created_at 자동 저장

**Files:**
- Modify: `app.py`
- Modify: `tests/test_board.py`
- Create: `templates/write.html`

- [ ] **Step 1: Write failing tests for write form, save, validation**

```python
# tests/test_board.py 에 아래 코드 추가

def test_write_page_renders_form(client):
    response = client.get("/write")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "name=\"title\"" in html
    assert "name=\"content\"" in html


def test_write_post_saves_and_redirects_to_detail(client):
    response = client.post(
        "/write",
        data={"title": "저장 테스트", "content": "저장된 본문"},
        follow_redirects=False,
    )

    assert response.status_code == 302
    location = response.headers["Location"]
    assert "/posts/" in location

    detail = client.get(location)
    html = detail.get_data(as_text=True)
    assert detail.status_code == 200
    assert "저장 테스트" in html
    assert "저장된 본문" in html


def test_write_post_rejects_blank_input(client):
    response = client.post(
        "/write",
        data={"title": "   ", "content": ""},
        follow_redirects=True,
    )
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "제목과 본문을 입력해주세요" in html
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_board.py::test_write_page_renders_form tests/test_board.py::test_write_post_saves_and_redirects_to_detail tests/test_board.py::test_write_post_rejects_blank_input -v`
Expected: FAIL (`/write` 라우트 미구현)

- [ ] **Step 3: Implement write GET/POST with validation and redirect**

```python
# app.py 에 추가/수정
from datetime import datetime
from flask import Flask, render_template, abort, request, redirect, url_for


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
```

```html
<!-- templates/write.html -->
{% extends "base.html" %}
{% block title %}글쓰기{% endblock %}
{% block content %}
  <h1>글쓰기</h1>

  {% if error %}
    <p>{{ error }}</p>
  {% endif %}

  <form method="post" action="{{ url_for('write_post') }}">
    <div>
      <label for="title">제목</label>
      <input id="title" name="title" type="text" value="{{ title }}" />
    </div>
    <div>
      <label for="content">본문</label>
      <textarea id="content" name="content" rows="10">{{ content }}</textarea>
    </div>
    <button type="submit">저장</button>
  </form>
{% endblock %}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_board.py::test_write_page_renders_form tests/test_board.py::test_write_post_saves_and_redirects_to_detail tests/test_board.py::test_write_post_rejects_blank_input -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add app.py templates/write.html tests/test_board.py
git commit -m "feat: add post creation flow with server-side validation"
```

---

### Task 4: 디자인 적용(3개 시안 혼합) + 전체 회귀 테스트

**Files:**
- Create: `static/style.css`
- Modify: `templates/base.html`
- Modify: `templates/list.html`
- Modify: `templates/detail.html`
- Modify: `templates/write.html`
- Modify: `tests/test_board.py`

- [ ] **Step 1: Write failing tests for shared layout/style hooks**

```python
# tests/test_board.py 에 아래 코드 추가

def test_pages_include_shared_navigation_and_stylesheet(client):
    list_html = client.get("/").get_data(as_text=True)
    write_html = client.get("/write").get_data(as_text=True)

    assert "href=\"/static/style.css\"" in list_html
    assert "href=\"/static/style.css\"" in write_html
    assert "Warm Journal" in list_html
    assert "목록" in list_html
    assert "글쓰기" in list_html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_board.py::test_pages_include_shared_navigation_and_stylesheet -v`
Expected: FAIL (현재 base 템플릿에 CSS 링크/브랜드 텍스트 없음)

- [ ] **Step 3: Implement beige/minimal UI across templates**

```css
/* static/style.css */
:root {
  --bg: #fcf9f5;
  --paper: #f7f3f0;
  --text: #1c1c1a;
  --muted: #6b6a61;
  --line: #d9d4cf;
  --accent: #79564b;
  --accent-strong: #5e604d;
}

* { box-sizing: border-box; }

body {
  margin: 0;
  font-family: "Work Sans", system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
}

a { color: inherit; text-decoration: none; }

.site-header {
  position: sticky;
  top: 0;
  background: #f5f5dc;
  border-bottom: 1px solid var(--line);
}

.container {
  max-width: 1120px;
  margin: 0 auto;
  padding: 20px;
}

.nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 64px;
}

.brand {
  font-family: "Plus Jakarta Sans", system-ui, sans-serif;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  gap: 20px;
  font-size: 14px;
}

.page-title {
  font-family: "Plus Jakarta Sans", system-ui, sans-serif;
  font-size: 32px;
  margin: 0 0 20px;
}

.card {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 18px;
  margin-bottom: 14px;
}

.card-title {
  font-family: "Plus Jakarta Sans", system-ui, sans-serif;
  font-size: 22px;
  margin: 0 0 8px;
}

.meta {
  color: var(--muted);
  font-size: 14px;
  margin-bottom: 12px;
}

.empty-state {
  background: var(--paper);
  border: 1px dashed var(--line);
  border-radius: 10px;
  padding: 24px;
}

.button {
  display: inline-block;
  background: var(--accent);
  color: #fff;
  border: 0;
  border-radius: 8px;
  padding: 10px 16px;
  font: inherit;
  cursor: pointer;
}

.button.secondary {
  background: transparent;
  color: var(--accent);
  border: 1px solid var(--accent);
}

.field {
  margin-bottom: 14px;
}

.field label {
  display: block;
  margin-bottom: 6px;
  color: var(--muted);
  font-size: 14px;
}

.field input,
.field textarea {
  width: 100%;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 10px 12px;
  background: #fff;
  font: inherit;
}

.error {
  border: 1px solid #e6b8b2;
  background: #fff2f1;
  color: #7d2c23;
  border-radius: 8px;
  padding: 10px 12px;
  margin-bottom: 12px;
}
```

```html
<!-- templates/base.html (전체 교체) -->
<!doctype html>
<html lang="ko">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{% block title %}Warm Journal{% endblock %}</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@600;700&family=Work+Sans:wght@400;500&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}" />
  </head>
  <body>
    <header class="site-header">
      <div class="container nav">
        <a class="brand" href="{{ url_for('list_posts') }}">Warm Journal</a>
        <nav class="nav-links">
          <a href="{{ url_for('list_posts') }}">목록</a>
          <a href="{{ url_for('write_post') }}">글쓰기</a>
        </nav>
      </div>
    </header>

    <main class="container">
      {% block content %}{% endblock %}
    </main>
  </body>
</html>
```

```html
<!-- templates/list.html (전체 교체) -->
{% extends "base.html" %}
{% block title %}게시글 목록{% endblock %}
{% block content %}
  <h1 class="page-title">게시글 목록</h1>

  {% if posts %}
    {% for post in posts %}
      <article class="card">
        <h2 class="card-title">
          <a href="{{ url_for('show_post', post_id=post['id']) }}">{{ post['title'] }}</a>
        </h2>
        <div class="meta">{{ post['created_at'] }}</div>
        <p>{{ post['content'][:140] }}{% if post['content']|length > 140 %}...{% endif %}</p>
      </article>
    {% endfor %}
  {% else %}
    <section class="empty-state">
      <p>아직 게시글이 없습니다</p>
      <a class="button" href="{{ url_for('write_post') }}">글쓰기</a>
    </section>
  {% endif %}
{% endblock %}
```

```html
<!-- templates/detail.html (전체 교체) -->
{% extends "base.html" %}
{% block title %}{{ post['title'] }}{% endblock %}
{% block content %}
  <article class="card">
    <h1 class="page-title">{{ post['title'] }}</h1>
    <div class="meta">{{ post['created_at'] }}</div>
    <div>{{ post['content']|replace('\n', '<br />')|safe }}</div>
    <p style="margin-top: 20px;">
      <a class="button secondary" href="{{ url_for('list_posts') }}">목록으로</a>
    </p>
  </article>
{% endblock %}
```

```html
<!-- templates/write.html (전체 교체) -->
{% extends "base.html" %}
{% block title %}글쓰기{% endblock %}
{% block content %}
  <h1 class="page-title">글쓰기</h1>

  {% if error %}
    <div class="error">{{ error }}</div>
  {% endif %}

  <form method="post" action="{{ url_for('write_post') }}">
    <div class="field">
      <label for="title">제목</label>
      <input id="title" name="title" type="text" value="{{ title }}" />
    </div>

    <div class="field">
      <label for="content">본문</label>
      <textarea id="content" name="content" rows="14">{{ content }}</textarea>
    </div>

    <button class="button" type="submit">저장</button>
  </form>
{% endblock %}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest -v`
Expected: PASS (모든 테스트 녹색)

- [ ] **Step 5: Manual UI check in browser**

Run:
- `python app.py`
- 브라우저에서 `http://127.0.0.1:5000/` 접속

체크 항목:
- 빈 상태 문구 + 글쓰기 버튼 노출
- 글쓰기 저장 후 상세 화면 이동
- 목록 카드가 최신순으로 보이는지 확인
- 잘못된 상세 URL(`/posts/99999`) 404 확인

- [ ] **Step 6: Commit**

```bash
git add static/style.css templates/base.html templates/list.html templates/detail.html templates/write.html tests/test_board.py
git commit -m "style: apply warm minimalist UI across list detail and write pages"
```
