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


def test_write_page_renders_form(client):
    response = client.get("/write")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'name="title"' in html
    assert 'name="content"' in html


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


def test_pages_include_shared_navigation_and_stylesheet(client):
    list_html = client.get("/").get_data(as_text=True)
    write_html = client.get("/write").get_data(as_text=True)

    assert 'href="/static/style.css"' in list_html
    assert 'href="/static/style.css"' in write_html
    assert "The Journal" in list_html
    assert "목록" in list_html
    assert "글쓰기" in list_html


def test_list_page_supports_three_view_variants(client):
    post_id = insert_post_for_test("목록 뷰", "목록 테스트 본문", "2026-04-25 12:00:00")

    sidebar_html = client.get("/?view=sidebar").get_data(as_text=True)
    center_html = client.get("/?view=center").get_data(as_text=True)
    split_html = client.get("/?view=split").get_data(as_text=True)

    assert post_id
    assert "Sidebar" in sidebar_html
    assert "Center" in center_html
    assert "Split" in split_html
    assert "list-sidebar-layout" in sidebar_html
    assert "list-center-layout" in center_html
    assert "list-split-layout" in split_html
