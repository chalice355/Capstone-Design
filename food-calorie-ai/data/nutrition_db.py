"""
전국통합식품영양성분정보표준데이터 CSV → SQLite import
출처: 공공데이터포털 (https://www.data.go.kr/data/15100064/standard.do)

- API 키 불필요
- 오프라인 완전 동작
- 5만 건 로컬 조회

사용법:
  python data/nutrition_db.py --csv 전국통합식품영양성분정보표준데이터.csv
"""

import sqlite3
import pandas as pd
import os
import argparse

DB_PATH  = os.path.join(os.path.dirname(__file__), "food_nutrition.db")

# CSV 컬럼 → DB 컬럼 매핑
COL_MAP = {
    "식품코드":     "food_code",
    "식품명":       "food_name",
    "에너지(kcal)": "calories",
    "탄수화물(g)":  "carbs",
    "당류(g)":      "sugar",
    "식이섬유(g)":  "fiber",
    "단백질(g)":    "protein",
    "지방(g)":      "fat",
    "포화지방산(g)":"saturated_fat",
    "트랜스지방산(g)":"trans_fat",
    "나트륨(mg)":   "sodium",
    "콜레스테롤(mg)":"cholesterol",
    "칼슘(mg)":     "calcium",
    "영양성분함량기준량": "serving_size",
}


def init_db(conn: sqlite3.Connection):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nutrition (
            food_code     TEXT PRIMARY KEY,
            food_name     TEXT NOT NULL,
            serving_size  TEXT,
            calories      REAL,
            carbs         REAL,
            sugar         REAL,
            fiber         REAL,
            protein       REAL,
            fat           REAL,
            saturated_fat REAL,
            trans_fat     REAL,
            sodium        REAL,
            cholesterol   REAL,
            calcium       REAL
        )
    """)
    conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_food_name ON nutrition (food_name)"
    )
    conn.commit()


def import_csv(csv_path: str):
    """CSV 파일을 읽어 SQLite에 전량 저장"""
    print(f"CSV 로드 중: {csv_path}")
    df = pd.read_csv(csv_path, encoding="cp949", on_bad_lines="skip", low_memory=False)

    # 필요한 컬럼만 추출
    existing_cols = [c for c in COL_MAP if c in df.columns]
    df = df[existing_cols].rename(columns=COL_MAP)

    # 숫자형 변환 (문자 섞인 값 → NaN)
    numeric_cols = [c for c in df.columns if c not in ("food_code", "food_name", "serving_size")]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["food_name", "calories"])

    conn = sqlite3.connect(DB_PATH)
    init_db(conn)
    df.to_sql("nutrition", conn, if_exists="replace", index=False)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_food_name ON nutrition (food_name)")
    conn.commit()
    conn.close()

    print(f"✅ import 완료: {len(df):,}건 → {DB_PATH}")


def get_nutrition(food_name: str) -> dict | None:
    """
    음식명으로 영양 정보 조회.
    완전 일치 → 없으면 부분 일치 첫 번째 반환.
    """
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            "DB 없음. 먼저 실행하세요:\n"
            "  python data/nutrition_db.py --csv 전국통합식품영양성분정보표준데이터.csv"
        )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    # 1) 완전 일치
    row = conn.execute(
        "SELECT * FROM nutrition WHERE food_name = ? LIMIT 1", (food_name,)
    ).fetchone()

    # 2) 부분 일치
    if row is None:
        row = conn.execute(
            "SELECT * FROM nutrition WHERE food_name LIKE ? LIMIT 1",
            (f"%{food_name}%",)
        ).fetchone()

    conn.close()
    return dict(row) if row else None


def search_foods(keyword: str, limit: int = 10) -> list[dict]:
    """키워드로 음식 목록 검색 (앱 자동완성용)"""
    if not os.path.exists(DB_PATH):
        return []
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT food_name, calories, serving_size FROM nutrition "
        "WHERE food_name LIKE ? LIMIT ?",
        (f"%{keyword}%", limit)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="식품영양 CSV → SQLite import")
    parser.add_argument(
        "--csv", required=True,
        help="전국통합식품영양성분정보표준데이터.csv 경로"
    )
    args = parser.parse_args()
    import_csv(args.csv)
