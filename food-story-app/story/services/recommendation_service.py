import os
import json
import re
import requests
from google import genai
from pathlib import Path
from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path)

_client = None

NAVER_IMAGE_URL = "https://openapi.naver.com/v1/search/image"


def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
    return _client


def _get_image_url(food_name: str) -> str:
    headers = {
        "X-Naver-Client-Id":     os.getenv("NAVER_CLIENT_ID"),
        "X-Naver-Client-Secret": os.getenv("NAVER_CLIENT_SECRET"),
    }
    params = {"query": food_name, "display": 1, "sort": "sim"}
    try:
        res = requests.get(NAVER_IMAGE_URL, headers=headers, params=params, timeout=5)
        items = res.json().get("items", [])
        if items:
            return items[0].get("thumbnail", "")
    except Exception as e:
        print(f"[ERROR] 이미지 검색 실패 ({food_name}): {e}")
    return ""


def get_recommendations(food_name: str) -> list:
    prompt = (
        f"'{food_name}'와 잘 어울리거나 연관된 한국 음식 3가지를 추천해줘. "
        "각 음식의 이름과 1~2문장 짧은 설명을 JSON 배열로만 반환해줘. "
        '형식 예시: [{"name": "잡채", "description": "당면과 채소를 볶아 만든 명절 음식이에요."}] '
        "JSON 외의 텍스트, 마크다운 코드블록, 주석은 포함하지 마."
    )

    response = _get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    text = response.text.strip()
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if not match:
        print(f"[ERROR] JSON 파싱 실패: {text[:200]}")
        return []

    try:
        foods = json.loads(match.group())
    except json.JSONDecodeError as e:
        print(f"[ERROR] JSON 디코딩 실패: {e}")
        return []

    result = []
    for food in foods[:3]:
        name = food.get("name", "").strip()
        desc = food.get("description", "").strip()
        if not name:
            continue
        image_url = _get_image_url(name)
        result.append({"name": name, "description": desc, "image_url": image_url})

    return result
