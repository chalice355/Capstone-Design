import os
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv
from pathlib import Path
from .summary_service import summarize_tab
from .recommendation_service import get_recommendations

_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path)

NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
SEARCH_URL          = "https://openapi.naver.com/v1/search/webkr.json"

SEARCH_QUERIES = {
    "유래":   "{food} 유래 역사 기원",
    "술":     "{food} 어울리는 술 소주 막걸리 맥주 와인 페어링 추천",
    "이야기": "{food} 문화 이야기 속담 에피소드",
    "노래":   "{food} 노래",
    "미디어": "{food} 등장하는 영화 드라마 책",
    "추천":   None,  # Gemini + Naver 이미지 검색으로 별도 처리
}


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def _naver_search(query: str, num: int = 3) -> list[dict]:
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print(f"[ERROR] 환경변수 누락 — NAVER_CLIENT_ID={bool(NAVER_CLIENT_ID)}")
        return []

    headers = {
        "X-Naver-Client-Id":     NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }
    params = {"query": query, "display": num, "sort": "sim"}

    try:
        res = requests.get(SEARCH_URL, headers=headers, params=params, timeout=5)
        if res.status_code != 200:
            print(f"[ERROR] Naver API 응답 {res.status_code}: {res.text}")
            return []
        return [
            {
                "title":   _strip_html(item.get("title", "")),
                "snippet": _strip_html(item.get("description", "")),
                "link":    item.get("link", ""),
            }
            for item in res.json().get("items", [])
        ]
    except Exception as e:
        print(f"[ERROR] Naver 검색 예외: {e}")
        return []


def get_tab_content(food_name: str, tab: str):
    if tab == "추천":
        return get_recommendations(food_name)

    query = SEARCH_QUERIES.get(tab, "{food} 관련 정보").format(food=food_name)
    items = _naver_search(query, num=7 if tab == "노래" else 3)

    if not items:
        return f"{food_name}의 {tab} 정보를 찾지 못했어요."

    if tab in ("미디어", "노래"):
        return [
            {"title": item["title"], "description": item["snippet"], "link": item["link"]}
            for item in items
        ]

    raw = "\n\n".join(
        f"제목: {item['title']}\n내용: {item['snippet']}" for item in items
    )
    return summarize_tab(food_name, tab, raw)


def get_all_tabs(food_name: str) -> dict:
    result = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(get_tab_content, food_name, tab): tab
            for tab in SEARCH_QUERIES
        }
        for future in as_completed(futures):
            tab = futures[future]
            try:
                result[tab] = future.result()
            except Exception as e:
                result[tab] = f"정보를 불러오지 못했어요. ({e})"
    return result
