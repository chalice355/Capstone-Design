import os
from google import genai
from google.genai import types
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path)

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    return _client


def identify_food(image_bytes: bytes, media_type: str = "image/jpeg") -> str:
    response = _get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=media_type),
            "이 사진에 있는 음식 이름을 한국어로 딱 한 단어만 답해줘. 음식이 없으면 '알수없음'이라고만 답해줘.",
        ],
    )
    return response.text.strip()
