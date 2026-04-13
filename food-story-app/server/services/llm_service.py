import os
import re
import requests
from dotenv import load_dotenv
from pathlib import Path

_env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_env_path)

NAVER_CLIENT_ID     = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
SEARCH_URL          = "https://openapi.naver.com/v1/search/webkr.json"

SEARCH_QUERIES = {
    "유래":   "{food} 유래 역사 기원",
    "술":     "{food} 어울리는 술 주류 페어링",
    "이야기": "{food} 문화 이야기 속담 에피소드",
    "노래":   "{food} 어울리는 노래 음악 추천",
    "미디어": "{food} 등장하는 영화 드라마 책",
}


def _strip_html(text: str) -> str:
    """Naver 응답의 <b> 등 HTML 태그 제거"""
    return re.sub(r"<[^>]+>", "", text)


def _naver_search(query: str, num: int = 3) -> list[dict]:
    """Naver 검색 API 호출 → 결과 리스트 반환"""
    if not NAVER_CLIENT_ID or not NAVER_CLIENT_SECRET:
        print(f"[ERROR] 환경변수 누락 — NAVER_CLIENT_ID={bool(NAVER_CLIENT_ID)}, NAVER_CLIENT_SECRET={bool(NAVER_CLIENT_SECRET)}")
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
        items = res.json().get("items", [])
        return [
            {
                "title":   _strip_html(item.get("title", "")),
                "snippet": _strip_html(item.get("description", ""))[:100],
                "link":    item.get("link", ""),
            }
            for item in items
        ]
    except Exception as e:
        print(f"[ERROR] Naver 검색 예외: {e}")
        return []


def get_tab_content(food_name: str, tab: str):
    """탭별 검색어로 Naver 검색 → 결과 텍스트 반환"""
    query_template = SEARCH_QUERIES.get(tab, "{food} 관련 정보")
    query = query_template.format(food=food_name)
    items = _naver_search(query)

    if not items:
        return f"{food_name}의 {tab} 정보를 찾지 못했어요."

    if tab == "미디어":
        return [
            {"title": item["title"], "description": item["snippet"], "link": item["link"]}
            for item in items
        ]

    result = f"[{food_name} — {tab}]\n\n"
    for item in items:
        result += f"• {item['title']}\n"
        result += f"  {item['snippet']}\n\n"
    return result.strip()


def get_all_tabs(food_name: str) -> dict:
    """모든 탭 콘텐츠를 한 번에 조회"""
    result = {}
    for tab in SEARCH_QUERIES:
        try:
            result[tab] = get_tab_content(food_name, tab)
        except Exception as e:
            result[tab] = f"정보를 불러오지 못했어요. ({e})"
    return result
