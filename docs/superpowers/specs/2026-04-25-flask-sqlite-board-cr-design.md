# Flask + SQLite 게시판 C/R 디자인 스펙

## 1) 목표
`Design/stitch_simple_beige_blog_ui`의 3개 시안 무드를 혼합해 Flask + SQLite 기반 게시판 MVP를 만든다.
이번 범위는 C/R만 포함한다.

- C: 글쓰기
- R: 목록 보기
- R: 상세 보기
- 제외: 수정/삭제

## 2) 기술/구조
- Backend: Flask (단일 `app.py`)
- DB: SQLite (`board.db`)
- Template: Jinja2 (`templates/`)
- Style: `static/style.css` (공통 톤/타이포/컴포넌트)

파일 구성:
- `app.py`
- `templates/base.html`
- `templates/list.html`
- `templates/detail.html`
- `templates/write.html`
- `static/style.css`

## 3) 데이터 모델
테이블: `posts`
- `id INTEGER PRIMARY KEY AUTOINCREMENT`
- `title TEXT NOT NULL`
- `content TEXT NOT NULL`
- `created_at TEXT NOT NULL`

앱 시작 시 테이블이 없으면 생성한다.

## 4) 라우팅/기능
### `GET /`
- 게시글 목록 최신순(`id DESC`) 조회
- 데이터가 없으면 빈 상태 UI 표시
  - 문구: "아직 게시글이 없습니다"
  - 글쓰기 버튼 노출

### `GET /posts/<int:post_id>`
- 단건 조회 후 상세 렌더링
- 존재하지 않으면 404 반환

### `GET /write`
- 글쓰기 폼 렌더링
- 입력 필드: `title`, `content`

### `POST /write`
- 서버 측 필수 검증(`title`, `content` 공백 불가)
- 검증 실패 시 동일 폼 재렌더링 + 에러 메시지
- 성공 시 DB 저장
  - `created_at`은 서버 현재시각 자동 저장
- 저장 후 상세 페이지(`/posts/<id>`)로 리다이렉트

## 5) UI 디자인 적용 원칙
3개 시안의 요소를 혼합해 일관된 beige/minimal 감성을 유지한다.

- 목록: 카드형 리스트 + 넉넉한 여백 + warm neutral 색상
- 상세: 본문 중심 + 보조 메타 정보 + 읽기 편한 타이포
- 글쓰기: 단순 입력 레이아웃 + 명확한 CTA
- 공통: 상단 내비, 컨테이너 폭 제한, 라운드/보더 최소 강조

## 6) 에러/검증
- 입력값 검증 실패: 사용자 친화적 메시지 표시
- 없는 게시글 접근: 404 텍스트 응답(간단 버전)

## 7) 검증 시나리오
1. 글쓰기 성공 후 상세 페이지 이동
2. 목록 페이지 최신순 노출 확인
3. 빈 상태 UI 노출 확인
4. 잘못된 post id 접근 시 404 확인

## 8) 구현 범위 명확화
- 이번 단계에서 수정/삭제 라우트 및 UI는 만들지 않는다.
- 이후 단계에서 Update/Delete를 별도 추가한다.
