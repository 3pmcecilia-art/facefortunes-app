# PRD Step 1 — 얼굴 이미지 입력 및 인식

## 목표
사용자가 업로드한 사진에서 얼굴을 감지하고, `qwen/qwen3.5-flash-02-23` 모델을 통해 얼굴의 주요 특징을 구조화된 데이터로 추출한다.

---

## 사용자 스토리
- 사용자는 웹 페이지에서 자신의 사진을 업로드하거나 카메라로 촬영할 수 있다.
- 업로드 즉시 얼굴 감지 여부를 확인하고, 인식된 특징 요약을 볼 수 있다.

---

## 기능 요구사항

### 1-1. 이미지 입력 UI
| 항목 | 내용 |
|------|------|
| 입력 방식 | 파일 업로드 (drag & drop 포함), 카메라 촬영(모바일) |
| 허용 형식 | JPG, PNG, WEBP (최대 10MB) |
| 미리보기 | 업로드 후 이미지 썸네일 즉시 표시 |
| 재업로드 | 언제든 다른 이미지로 교체 가능 |

### 1-2. 얼굴 인식 API 호출
- **모델:** `qwen/qwen3.5-flash-02-23`
- **엔드포인트:** `POST https://openrouter.ai/api/v1/chat/completions`
- **입력:** 이미지를 base64로 인코딩하여 `image_url` content 타입으로 전달
- **시스템 프롬프트 지침:**
  - 얼굴이 없으면 명확히 오류 반환
  - 얼굴이 여러 명이면 가장 크게 보이는 얼굴 1명만 분석
  - 긍정적·중립적 표현만 사용, 부정적 외모 묘사 금지

### 1-3. 추출 데이터 구조 (JSON)
모델에게 아래 형식의 JSON을 반환하도록 프롬프트 지시:

```json
{
  "face_detected": true,
  "features": {
    "overall_shape": "계란형",
    "forehead": "넓고 반듯함",
    "eyes": "크고 선명한 쌍꺼풀, 눈빛이 또렷함",
    "nose": "콧대가 곧고 콧망울이 둥근 편",
    "mouth": "입술이 도톰하고 입꼬리가 자연스럽게 올라감",
    "chin": "적당히 갸름한 턱선",
    "eyebrows": "자연스러운 아치형",
    "cheekbones": "적당히 도드라짐",
    "skin_tone": "밝고 균일한 피부톤",
    "overall_impression": "온화하고 지적인 인상"
  },
  "confidence": 0.92
}
```

### 1-4. 오류 처리
| 상황 | 처리 |
|------|------|
| 얼굴 미감지 | "얼굴을 찾을 수 없습니다. 정면 사진을 올려주세요." 안내 |
| 이미지 품질 불량 | "더 선명한 사진을 업로드해주세요." 안내 |
| API 오류 | 재시도 버튼 제공, 에러 코드 표시 |
| 파일 크기 초과 | 업로드 전 클라이언트 사이드에서 차단 |

---

## API 프롬프트 설계

**System:**
```
You are a facial feature analyst. Analyze the face in the image and return ONLY a JSON object with the structure provided. Use positive and neutral Korean descriptions only. Never use negative or unflattering descriptions. If no face is detected, return {"face_detected": false}.
```

**User:**
```
다음 이미지에서 얼굴 특징을 분석해주세요. 반드시 아래 JSON 형식으로만 답변하세요: {"face_detected": true/false, "features": {"overall_shape": ..., "forehead": ..., "eyes": ..., "nose": ..., "mouth": ..., "chin": ..., "eyebrows": ..., "cheekbones": ..., "skin_tone": ..., "overall_impression": ...}, "confidence": 0.0~1.0}
```

---

## 기술 스택
- **Frontend:** HTML5 + Vanilla JS (또는 React)
- **Backend:** Python FastAPI
- **이미지 처리:** base64 인코딩 (PIL/Pillow로 리사이즈 후 전송)
- **이미지 최적화:** 전송 전 최대 1024px로 리사이즈

---

## 완료 기준 (Definition of Done)
- [ ] 이미지 업로드 UI 구현 완료
- [ ] qwen 모델 호출 및 JSON 파싱 성공
- [ ] 얼굴 미감지 시 사용자 안내 메시지 표시
- [ ] 추출된 특징 데이터가 Step 2로 전달 가능한 형태로 저장
