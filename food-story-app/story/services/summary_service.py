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


_TAB_PROMPTS = {
    "유래": (
        "위 내용을 바탕으로 '{food}'의 유래와 역사적 기원을 3~5문장으로 자연스럽게 요약해줘. "
        "핵심 내용만 친근한 말투로 써줘."
    ),
    "술": (
        "위 내용을 참고해서 '{food}'와 어울리는 술을 추천해줘. "
        "소주, 막걸리, 맥주, 와인, 사케 등 구체적인 술 이름을 중심으로 "
        "왜 잘 어울리는지 이유를 곁들여 4~6문장으로 써줘. "
        "검색 결과에 관련 내용이 부족하면 음식의 특성에 맞게 자유롭게 추천해줘."
    ),
    "이야기": (
        "위 내용을 바탕으로 '{food}'에 얽힌 문화적 이야기, 속담, 에피소드를 "
        "6~10문장으로 풍부하게 써줘. 흥미롭고 친근한 말투로 써줘."
    ),
    "노래": (
        "위 검색 결과에 나온 '{food}' 관련 노래들을 소개해줘. "
        "노래 제목과 가수명을 정확히 언급하고, 각 노래의 분위기나 특징을 간략히 설명해줘. "
        "6~8문장으로 친근한 말투로 써줘."
    ),
}


def summarize_tab(food_name: str, tab: str, raw_text: str) -> str:
    instruction = _TAB_PROMPTS.get(
        tab,
        "위 내용을 바탕으로 3~5문장으로 자연스럽게 요약해줘. 친근한 말투로 써줘."
    ).replace("{food}", food_name)

    prompt = (
        f"다음은 '{food_name}'의 '{tab}'에 관한 검색 결과야.\n\n"
        f"{raw_text}\n\n"
        f"{instruction} 출처나 링크는 포함하지 마."
    )

    response = _get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return response.text.strip()
