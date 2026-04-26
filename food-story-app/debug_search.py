"""Naver 검색 API 진단 스크립트
실행: python food-story-app/debug_search.py  (food-story-app-server 폴더에서)
"""
import os
import re
import requests
from pathlib import Path
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

client_id     = os.getenv("NAVER_CLIENT_ID")
client_secret = os.getenv("NAVER_CLIENT_SECRET")

print(f"[1] NAVER_CLIENT_ID 로드됨:     {bool(client_id)}")
print(f"[1] NAVER_CLIENT_SECRET 로드됨: {bool(client_secret)}")

if not client_id or not client_secret:
    print("[FAIL] 환경변수 누락 — .env 파일을 확인하세요.")
    raise SystemExit(1)

res = requests.get(
    "https://openapi.naver.com/v1/search/webkr.json",
    headers={"X-Naver-Client-Id": client_id, "X-Naver-Client-Secret": client_secret},
    params={"query": "비빔밥 유래 역사", "display": 3, "sort": "sim"},
    timeout=10,
)

print(f"\n[2] HTTP 상태코드: {res.status_code}")

if res.status_code != 200:
    print(f"[FAIL] 오류 응답: {res.text}")
    raise SystemExit(1)

items = res.json().get("items", [])
print(f"[3] 검색 결과 수: {len(items)}")

for i, item in enumerate(items, 1):
    title = re.sub(r"<[^>]+>", "", item.get("title", ""))
    desc  = re.sub(r"<[^>]+>", "", item.get("description", ""))
    print(f"\n  [{i}] {title}")
    print(f"       {desc[:80]}...")

print("\n[SUCCESS] Naver 검색 API 정상 작동!")
