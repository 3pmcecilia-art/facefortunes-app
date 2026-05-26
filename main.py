import os
import base64
import json
import re
from io import BytesIO

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    timeout=180.0,
)

SYSTEM_PROMPT = """당신은 얼굴 특징 분석 전문가입니다. 이미지의 얼굴을 분석하고 반드시 JSON 객체만 반환하세요.
- 모든 값은 반드시 한국어로 작성하세요.
- 긍정적이고 희망적인 표현만 사용하고, 부정적인 묘사는 절대 사용하지 마세요.
- 얼굴이 감지되지 않으면 정확히 {"face_detected": false} 만 반환하세요.
- 얼굴이 감지되면 다른 텍스트 없이 아래 구조만 반환하세요:
{"face_detected": true, "features": {"overall_shape": "...", "forehead": "...", "eyes": "...", "nose": "...", "mouth": "...", "chin": "...", "eyebrows": "...", "cheekbones": "...", "skin_tone": "...", "overall_impression": "..."}, "confidence": 0.0~1.0}"""

USER_PROMPT = """이미지에서 얼굴 특징을 분석해주세요.
- 모든 설명은 반드시 한국어로 작성하세요.
- 얼굴이 여러 명이면 가장 크게 보이는 얼굴 1명만 분석하세요.
- 모든 묘사는 긍정적이고 희망적인 표현을 사용하세요.
- JSON 형식으로만 답변하고 다른 텍스트는 포함하지 마세요."""


def resize_image(image_bytes: bytes, max_px: int = 1024) -> str:
    img = Image.open(BytesIO(image_bytes))
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    img.thumbnail((max_px, max_px), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return base64.b64encode(buf.getvalue()).decode()


def extract_json(text: str) -> dict:
    # 마크다운 코드블록 제거
    text = re.sub(r"```(?:json)?", "", text).strip()
    # JSON 객체 추출
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())
    raise ValueError("JSON을 파싱할 수 없습니다.")


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/reading")
async def reading_page():
    return FileResponse("static/reading.html")


@app.post("/api/analyze")
async def analyze_face(file: UploadFile = File(...)):
    # 파일 형식 검증
    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=400, detail="JPG, PNG, WEBP 형식만 허용됩니다.")

    image_bytes = await file.read()

    # 파일 크기 검증 (10MB)
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="파일 크기는 10MB 이하여야 합니다.")

    # 이미지 리사이즈 및 base64 인코딩
    b64 = resize_image(image_bytes)
    data_url = f"data:image/jpeg;base64,{b64}"

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.5-flash-02-23",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": data_url}},
                        {"type": "text", "text": USER_PROMPT},
                    ],
                },
            ],
            max_tokens=1024,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI 모델 호출 실패: {str(e)}")

    raw = response.choices[0].message.content

    try:
        result = extract_json(raw)
    except Exception:
        raise HTTPException(status_code=500, detail="AI 응답 파싱 실패. 다시 시도해주세요.")

    if not result.get("face_detected"):
        return {"face_detected": False, "message": "얼굴을 찾을 수 없습니다. 정면 사진을 올려주세요."}

    return result


# ── Step 2: 관상 풀이 ─────────────────────────────────────────────────────────

NEGATIVE_KEYWORDS = ["단점", "나쁜", "불운", "흉상", "못생", "결점", "단명", "흉격", "빈상", "박복"]

READING_SYSTEM_PROMPT = """당신은 한국 전통 관상학의 대가입니다. 제공된 얼굴 특징을 바탕으로 긍정적이고 희망적인 관상 풀이를 한국어로 작성하세요.

규칙:
1. 외모나 성격에 대한 부정적 묘사는 절대 사용하지 마세요.
2. 가능성, 강점, 기회에 집중하세요.
3. 모든 카테고리는 희망적이고 건설적이어야 합니다.
4. 반드시 유효한 JSON만 반환하고 다른 텍스트는 포함하지 마세요.
5. 각 카테고리 content는 2~3문장으로 작성하세요.
6. keywords는 각 카테고리당 2~3개의 핵심 단어 배열로 작성하세요."""

READING_USER_TEMPLATE = """다음 얼굴 특징을 바탕으로 관상을 풀이해 주세요.

얼굴 특징:
{features_json}

아래 JSON 구조로만 답변하세요:
{{
  "summary": "한 줄 요약",
  "categories": {{
    "personality": {{"title": "성격 및 기질", "content": "...", "keywords": ["키워드1", "키워드2"]}},
    "wealth":      {{"title": "재운 및 사업운", "content": "...", "keywords": ["키워드1", "키워드2"]}},
    "health":      {{"title": "건강운",        "content": "...", "keywords": ["키워드1", "키워드2"]}},
    "relationships":{{"title": "대인관계 및 애정운", "content": "...", "keywords": ["키워드1", "키워드2"]}},
    "career":      {{"title": "적성 및 직업운", "content": "...", "keywords": ["키워드1", "키워드2"]}}
  }},
  "lucky": {{"color": "색상명", "number": 숫자, "direction": "방향"}},
  "closing_message": "긍정적인 마무리 메시지"
}}"""


class ReadingRequest(BaseModel):
    features: dict


def has_negative_content(text: str) -> bool:
    return any(kw in text for kw in NEGATIVE_KEYWORDS)


@app.post("/api/reading")
async def get_reading(req: ReadingRequest):
    features_json = json.dumps(req.features, ensure_ascii=False, indent=2)
    user_prompt = READING_USER_TEMPLATE.format(features_json=features_json)

    try:
        response = client.chat.completions.create(
            model="google/gemma-3-27b-it:free",
            messages=[
                {"role": "system", "content": READING_SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=1024,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"관상 풀이 모델 호출 실패: {str(e)}")

    raw = response.choices[0].message.content

    try:
        result = extract_json(raw)
    except Exception:
        raise HTTPException(status_code=500, detail="관상 풀이 응답 파싱 실패. 다시 시도해주세요.")

    # 부정적 키워드 필터링
    result_text = json.dumps(result, ensure_ascii=False)
    if has_negative_content(result_text):
        raise HTTPException(status_code=500, detail="콘텐츠 안전 검사 실패. 다시 시도해주세요.")

    return result


app.mount("/static", StaticFiles(directory="static"), name="static")
