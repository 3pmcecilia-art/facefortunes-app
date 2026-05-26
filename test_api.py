import os, sys
sys.stdout.reconfigure(encoding="utf-8")
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENROUTER_API_KEY")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY,
)

# ── 1. 텍스트 테스트 ──────────────────────────────────────────────────────────
print("=" * 55)
print("[1] 텍스트 테스트  |  nvidia/nemotron-3-super-120b-a12b:free")
print("=" * 55)

text_resp = client.chat.completions.create(
    model="nvidia/nemotron-3-super-120b-a12b:free",
    messages=[
        {"role": "user", "content": "안녕하세요! 간단히 자기소개를 해주세요. (2~3문장)"}
    ],
    max_tokens=1024,
)
print("응답:", text_resp.choices[0].message.content)
print()

# ── 2. 이미지 테스트 ──────────────────────────────────────────────────────────
print("=" * 55)
print("[2] 이미지 테스트  |  qwen/qwen3.5-flash-02-23")
print("=" * 55)

image_url = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/"
    "PNG_transparency_demonstration_1.png/280px-PNG_transparency_demonstration_1.png"
)

img_resp = client.chat.completions.create(
    model="qwen/qwen3.5-flash-02-23",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": image_url}},
                {"type": "text", "text": "이 이미지에 무엇이 있나요? 간단히 설명해주세요."},
            ],
        }
    ],
)
print("응답:", img_resp.choices[0].message.content)
print()
print("[OK] 두 모델 모두 정상 응답 확인 완료.")
