"""
TheCocktailDB 오픈API 연동 및 SQLite 저장
API 문서: https://www.thecocktaildb.com/api.php
키 불필요 - 완전 무료
"""

import sqlite3
import requests
import json
import random
import os

DB_PATH  = os.path.join(os.path.dirname(__file__), "cocktail.db")
BASE_URL = "https://www.thecocktaildb.com/api/json/v1/1"

# 인식된 주류명 → API 검색어 매핑
SPIRIT_MAP = {
    "Vodka": "vodka", "Whiskey": "whiskey", "Rum": "rum",
    "Gin": "gin", "Tequila": "tequila", "Brandy": "brandy",
    "Beer": "beer", "Wine": "wine", "Triple Sec": "triple sec",
    "Vermouth": "vermouth", "Kahlua": "kahlua", "Baileys": "baileys",
}


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cocktails (
            cocktail_id   TEXT PRIMARY KEY,
            name          TEXT,
            base_spirit   TEXT,
            description   TEXT,
            ingredients   TEXT,
            instructions  TEXT,
            thumbnail_url TEXT
        )
    """)
    conn.commit()
    conn.close()


def _parse_cocktail(item: dict, spirit: str) -> dict:
    ingredients = []
    for i in range(1, 16):
        ing = item.get(f"strIngredient{i}", "")
        msr = item.get(f"strMeasure{i}", "")
        if ing:
            ingredients.append({"ingredient": ing.strip(), "measure": (msr or "").strip()})
    return {
        "cocktail_id":   item["idDrink"],
        "name":          item["strDrink"],
        "base_spirit":   spirit,
        "description":   item.get("strDrinkThumb", ""),   # 썸네일로 대체, 별도 설명 없음
        "ingredients":   json.dumps(ingredients, ensure_ascii=False),
        "instructions":  item.get("strInstructions") or "",
        "thumbnail_url": item.get("strDrinkThumb") or "",
    }


def fetch_and_store(spirit: str):
    keyword = SPIRIT_MAP.get(spirit, spirit.lower())
    url = f"{BASE_URL}/filter.php?i={keyword}"
    try:
        res   = requests.get(url, timeout=5)
        items = res.json().get("drinks") or []
    except Exception:
        return

    conn = sqlite3.connect(DB_PATH)
    for item in items[:20]:   # 최대 20개
        detail_res = requests.get(f"{BASE_URL}/lookup.php?i={item['idDrink']}", timeout=5)
        detail     = detail_res.json().get("drinks", [{}])[0]
        row        = _parse_cocktail(detail, spirit)
        conn.execute("""
            INSERT OR REPLACE INTO cocktails VALUES (?,?,?,?,?,?,?)
        """, tuple(row.values()))
    conn.commit()
    conn.close()


def get_cocktails_by_spirit(spirit: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT cocktail_id, name, thumbnail_url FROM cocktails WHERE base_spirit=?",
        (spirit,)
    ).fetchall()
    conn.close()

    if not rows:
        fetch_and_store(spirit)
        conn  = sqlite3.connect(DB_PATH)
        rows  = conn.execute(
            "SELECT cocktail_id, name, thumbnail_url FROM cocktails WHERE base_spirit=?",
            (spirit,)
        ).fetchall()
        conn.close()

    return [{"cocktail_id": r[0], "name": r[1], "thumbnail_url": r[2]} for r in rows]


def get_cocktail_detail(cocktail_id: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    row  = conn.execute(
        "SELECT name, base_spirit, description, ingredients, instructions, thumbnail_url "
        "FROM cocktails WHERE cocktail_id=?", (cocktail_id,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    ingredients = json.loads(row[3])
    instructions = row[4]
    # 한줄 설명 — 제조법 첫 문장 활용
    first_sentence = (instructions.split(".")[0] + ".") if instructions else "레시피를 확인하세요."

    return {
        "name":          row[0],
        "base_spirit":   row[1],
        "description":   first_sentence,
        "ingredients":   ingredients,
        "instructions":  instructions,
        "thumbnail_url": row[5],
    }


def get_random_cocktail() -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute("SELECT cocktail_id FROM cocktails").fetchall()
    conn.close()
    if not rows:
        return None
    random_id = random.choice(rows)[0]
    return get_cocktail_detail(random_id)


if __name__ == "__main__":
    init_db()
    print("DB 초기화 완료. 주요 주류 데이터 수집 중...")
    for spirit in SPIRIT_MAP:
        print(f"  → {spirit} 수집 중...")
        fetch_and_store(spirit)
    print("완료:", DB_PATH)
