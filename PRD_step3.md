# PRD Step 3 — 사용자 프로필 및 관상 히스토리

## 목표
관상 결과를 사용자 프로필에 저장하고, 과거 기록을 열람·관리할 수 있는 마이페이지를 제공한다. 회원가입 없이도 로컬 저장이 가능하며, 선택적으로 계정 생성 시 클라우드 저장을 지원한다.

---

## 사용자 스토리
- 사용자는 관상 결과 화면에서 "저장하기" 버튼을 눌러 결과를 보관할 수 있다.
- 마이페이지에서 과거 관상 기록 목록을 날짜순으로 볼 수 있다.
- 특정 기록을 클릭하면 상세 결과를 다시 열람할 수 있다.
- 원하지 않는 기록은 삭제할 수 있다.

---

## 기능 요구사항

### 3-1. 저장 데이터 구조

```json
{
  "record_id": "uuid-v4",
  "created_at": "2026-04-09T14:30:00Z",
  "nickname": "사용자가 입력한 이름 (선택)",
  "thumbnail": "base64 또는 blob URL (100x100px)",
  "step1_features": { },
  "step2_reading": { },
  "tags": ["재운", "리더십"]
}
```

### 3-2. 저장 방식

| 모드 | 저장 위치 | 조건 |
|------|-----------|------|
| 비회원 | 브라우저 `localStorage` | 기본값, 최대 10건 보관 |
| 회원 | 서버 DB (SQLite → PostgreSQL) | 이메일/소셜 로그인 후 |
| 내보내기 | JSON 파일 다운로드 | 언제든 가능 |

### 3-3. 프로필 UI 구성

#### 마이페이지 레이아웃
```
┌─────────────────────────────────┐
│  프로필 아바타  |  닉네임       │
│  총 분석 횟수: 5회              │
├─────────────────────────────────┤
│  [+ 새 관상 보기]               │
├─────────────────────────────────┤
│  히스토리 목록                  │
│  ┌──────────────────────────┐  │
│  │ 썸네일 | 날짜 | 요약 한줄 │  │
│  │        | 키워드 태그들   │  │
│  └──────────────────────────┘  │
│  (반복...)                      │
└─────────────────────────────────┘
```

#### 상세 기록 모달/페이지
- Step 2 결과 전체 재표시
- 저장 날짜, 사용자 메모 추가 기능
- 공유 · 삭제 버튼

### 3-4. 프로필 설정
| 항목 | 내용 |
|------|------|
| 닉네임 | 최대 20자, 언제든 변경 가능 |
| 아바타 | 가장 최근 분석 이미지 썸네일 자동 적용 또는 직접 업로드 |
| 알림 | (선택) 브라우저 푸시 알림 수신 동의 |
| 데이터 삭제 | 전체 기록 초기화 버튼 (확인 다이얼로그 필수) |

### 3-5. 비회원 → 회원 전환
- localStorage 데이터를 서버 DB로 마이그레이션
- 전환 시 "기존 기록 10건을 계정에 연동합니다" 안내

---

## 데이터베이스 스키마 (SQLite)

```sql
CREATE TABLE users (
    id          TEXT PRIMARY KEY,   -- UUID
    nickname    TEXT,
    email       TEXT UNIQUE,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE readings (
    id          TEXT PRIMARY KEY,   -- UUID
    user_id     TEXT REFERENCES users(id),
    thumbnail   BLOB,
    features    TEXT,               -- JSON string
    reading     TEXT,               -- JSON string
    memo        TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 기술 스택
| 레이어 | 기술 |
|--------|------|
| Frontend | HTML/CSS/JS, localStorage API |
| Backend | Python FastAPI |
| DB | SQLite (개발), PostgreSQL (프로덕션 옵션) |
| 인증 | JWT (선택적, 회원 기능 구현 시) |
| 이미지 저장 | DB BLOB 또는 로컬 파일시스템 |

---

## API 엔드포인트

| Method | Path | 설명 |
|--------|------|------|
| `POST` | `/api/readings` | 관상 기록 저장 |
| `GET` | `/api/readings` | 전체 목록 조회 |
| `GET` | `/api/readings/{id}` | 특정 기록 조회 |
| `DELETE` | `/api/readings/{id}` | 기록 삭제 |
| `PATCH` | `/api/profile` | 닉네임 수정 |

---

## 완료 기준 (Definition of Done)
- [ ] "저장하기" 버튼 클릭 시 localStorage에 기록 저장
- [ ] 마이페이지에서 히스토리 목록 렌더링
- [ ] 상세 기록 열람 및 삭제 기능 동작
- [ ] 최대 10건 초과 시 가장 오래된 기록 자동 제거 (비회원)
- [ ] JSON 내보내기 다운로드 기능 동작
