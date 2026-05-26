# PRD Step 2 — 관상 풀이

## 목표
Step 1에서 추출한 얼굴 특징 데이터를 `nvidia/nemotron-3-super-120b-a12b:free` 모델에 전달하여, 동양 관상학 기반의 긍정적·희망적 관상 해석을 생성한다.

---

## 사용자 스토리
- 사용자는 얼굴 분석 완료 후 자동으로 관상 풀이 화면으로 전환된다.
- 관상 결과는 여러 카테고리(성격, 재운, 건강, 대인관계, 적성)로 나누어 표시된다.
- 결과 화면은 보기 좋고 긍정적인 톤으로 구성되어 공유하고 싶어진다.

---

## 기능 요구사항

### 2-1. 관상 풀이 API 호출
- **모델:** `nvidia/nemotron-3-super-120b-a12b:free`
- **입력:** Step 1의 `features` JSON 객체
- **max_tokens:** 1024
- **호출 시점:** Step 1 JSON 수신 직후 자동 호출

### 2-2. 관상 결과 데이터 구조 (JSON)

```json
{
  "summary": "온화한 카리스마와 깊은 지혜를 지닌 인상입니다.",
  "categories": {
    "personality": {
      "title": "성격 및 기질",
      "content": "포용력이 크고 주변을 편안하게 만드는 기질을 타고났습니다...",
      "keywords": ["포용력", "지혜", "친화력"]
    },
    "wealth": {
      "title": "재운 및 사업운",
      "content": "꾸준한 노력으로 재물을 쌓는 형입니다...",
      "keywords": ["안정적 재운", "성실함", "신뢰"]
    },
    "health": {
      "title": "건강운",
      "content": "전반적으로 균형 잡힌 체질을 가지고 있습니다...",
      "keywords": ["균형", "지구력"]
    },
    "relationships": {
      "title": "대인관계 및 애정운",
      "content": "자연스럽게 사람들이 모여드는 인상입니다...",
      "keywords": ["인복", "신뢰", "매력"]
    },
    "career": {
      "title": "적성 및 직업운",
      "content": "창의성과 분석력을 함께 갖춘 타입으로...",
      "keywords": ["창의성", "분석력", "리더십"]
    }
  },
  "lucky": {
    "color": "딥 블루",
    "number": 7,
    "direction": "동쪽"
  },
  "closing_message": "당신의 얼굴에는 밝은 미래가 담겨 있습니다."
}
```

### 2-3. 결과 표시 UI
| 구성 요소 | 내용 |
|-----------|------|
| 상단 요약 카드 | 대표 한 줄 요약 + 이미지 썸네일 |
| 카테고리 탭/카드 | 성격 / 재운 / 건강 / 대인관계 / 적성 5개 섹션 |
| 키워드 태그 | 각 카테고리별 핵심 키워드 배지 |
| 행운 정보 | 행운의 색상 · 숫자 · 방향 |
| 마무리 메시지 | 긍정적 응원 문구 |
| 공유 버튼 | 결과 이미지로 캡처하여 SNS 공유 |

### 2-4. 콘텐츠 안전 정책
- 외모를 직접 비판하거나 부정적으로 묘사하는 문장 **절대 금지**
- "단점", "나쁜", "불운", "흉상" 등 부정적 단어 필터링
- 모든 해석은 가능성과 노력을 강조하는 방향으로 작성
- System 프롬프트에 안전 가이드라인 명시

---

## API 프롬프트 설계

**System:**
```
You are a master of Korean traditional physiognomy (관상학). Based on facial features provided, generate a positive, uplifting fortune reading in Korean.
Rules:
1. Never use negative descriptions about appearance or personality.
2. Focus on potential, strengths, and opportunities.
3. All five categories must be hopeful and constructive.
4. Return ONLY valid JSON matching the specified structure.
5. Each category content should be 2-3 sentences.
```

**User:**
```
다음 얼굴 특징을 바탕으로 관상을 풀이해 주세요.
얼굴 특징: {features_json}

아래 JSON 구조로만 답변해 주세요: { "summary": ..., "categories": { "personality": ..., "wealth": ..., "health": ..., "relationships": ..., "career": ... }, "lucky": { "color": ..., "number": ..., "direction": ... }, "closing_message": ... }
```

---

## 로딩 UX
- API 호출 중 로딩 애니메이션 표시 ("관상을 살펴보는 중입니다...")
- 예상 대기 시간: 3~8초
- 타임아웃: 30초 초과 시 재시도 안내

---

## 기술 스택
- Step 1과 동일한 FastAPI 백엔드에서 별도 엔드포인트 (`POST /api/reading`)
- Step 1 결과 JSON을 request body로 수신
- 응답 JSON을 프론트엔드에 그대로 전달

---

## 완료 기준 (Definition of Done)
- [ ] nemotron 모델 호출 및 JSON 파싱 성공
- [ ] 5개 카테고리 카드 UI 렌더링 완료
- [ ] 부정적 키워드 필터링 로직 동작 확인
- [ ] 공유용 결과 캡처 기능 구현
- [ ] Step 3 저장 버튼과 연결
