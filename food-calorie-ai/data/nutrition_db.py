"""
식약처 식품영양성분 오픈API 연동 및 SQLite 저장
API 키 발급: https://www.foodsafetykorea.go.kr/api/main.do
"""

import sqlite3
import requests
import os

API_KEY = os.environ.get("FOOD_API_KEY", "YOUR_API_KEY_HERE")
DB_PATH = os.path.join(os.path.dirname(__file__), "food_nutrition.db")
API_URL = "http://openapi.foodsafetykorea.go.kr/api/{key}/I2790/json/1/5/FOOD_NM_KR={name}"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nutrition (
            food_name TEXT PRIMARY KEY,
            calories  REAL,
            carbs     REAL,
            protein   REAL,
            fat       REAL
        )
    """)
    conn.commit()
    conn.close()


def fetch_from_api(food_name: str) -> dict | None:
    url = API_URL.format(key=API_KEY, name=food_name)
    try:
        res = requests.get(url, timeout=5)
        data = res.json().get("I2790", {}).get("row", [])
        if not data:
            return None
        row = data[0]
        return {
            "calories": float(row.get("AMT_NUM1") or 0),
            "carbs":    float(row.get("AMT_NUM7") or 0),
            "protein":  float(row.get("AMT_NUM3") or 0),
            "fat":      float(row.get("AMT_NUM4") or 0),
        }
    except Exception:
        return None


def get_nutrition(food_name: str) -> dict | None:
    """DB 캐시 우선 조회 → 없으면 API 호출 후 저장"""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT calories, carbs, protein, fat FROM nutrition WHERE food_name=?",
        (food_name,)
    ).fetchone()

    if row:
        conn.close()
        return {"calories": row[0], "carbs": row[1], "protein": row[2], "fat": row[3]}

    # API에서 가져와 캐싱
    nutrition = fetch_from_api(food_name)
    if nutrition:
        conn.execute(
            "INSERT OR REPLACE INTO nutrition VALUES (?,?,?,?,?)",
            (food_name, nutrition["calories"], nutrition["carbs"],
             nutrition["protein"], nutrition["fat"])
        )
        conn.commit()

    conn.close()
    return nutrition


if __name__ == "__main__":
    init_db()
    print("DB 초기화 완료:", DB_PATH)
