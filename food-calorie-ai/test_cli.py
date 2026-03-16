"""
빠른 동작 확인용 CLI 테스트 스크립트
Streamlit 없이 터미널에서 전체 흐름 확인

사용법:
  python test_cli.py                         # 더미 모델로 전체 흐름 확인
  python test_cli.py --image 음식사진.jpg    # 실제 사진으로 테스트
  python test_cli.py --apikey YOUR_KEY       # 식약처 API 키 입력
"""

import argparse
import os
import sys
import requests
import sqlite3
import json


# ────────────────────────────────────────────
# 1. 모델 추론 테스트
# ────────────────────────────────────────────
def test_model(image_path: str | None) -> str:
    print("\n" + "=" * 40)
    print("[ 1단계 ] 음식 인식 모델 테스트")
    print("=" * 40)

    model_path = os.path.join("model", "efficientnet_food.pth")

    if image_path is None or not os.path.exists(image_path):
        # 모델 파일 없을 때 → 더미 결과로 흐름 확인
        food_name = "비빔밥"
        confidence = 0.92
        print(f"  ℹ️  모델 파일 없음 → 더미 결과 사용")
        print(f"  결과: {food_name}  (신뢰도: {confidence:.1%})")
        return food_name

    try:
        import torch
        import torchvision.transforms as transforms
        from torchvision import models
        from PIL import Image

        class_names_path = os.path.join("model", "class_names.json")
        if not os.path.exists(class_names_path):
            print("  ❌ class_names.json 없음 → 먼저 model/train.py 실행 필요")
            sys.exit(1)

        with open(class_names_path, encoding="utf-8") as f:
            class_names = json.load(f)

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406],
                                 [0.229, 0.224, 0.225]),
        ])

        model = models.efficientnet_b0(weights=None)
        model.classifier[1] = torch.nn.Linear(
            model.classifier[1].in_features, len(class_names)
        )
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        model.eval()

        image = Image.open(image_path).convert("RGB")
        tensor = transform(image).unsqueeze(0)

        with torch.no_grad():
            outputs = model(tensor)
            probs   = torch.softmax(outputs, dim=1)
            conf, idx = probs.max(dim=1)

        food_name  = class_names[idx.item()]
        confidence = conf.item()
        print(f"  ✅ 인식 성공!")
        print(f"  결과: {food_name}  (신뢰도: {confidence:.1%})")
        return food_name

    except Exception as e:
        print(f"  ❌ 오류: {e}")
        sys.exit(1)


# ────────────────────────────────────────────
# 2. 식약처 API 테스트
# ────────────────────────────────────────────
def test_api(food_name: str, api_key: str) -> dict | None:
    print("\n" + "=" * 40)
    print("[ 2단계 ] 식약처 오픈API 연동 테스트")
    print("=" * 40)
    print(f"  검색어: {food_name}")

    if api_key == "DEMO":
        print("  ℹ️  API 키 없음 → 더미 영양 데이터 사용")
        nutrition = {
            "calories": 560, "protein": 18.0, "fat": 8.5,
            "carbs": 98.0,  "sugar": 6.2,   "sodium": 890.0,
            "saturated_fat": 1.8, "fiber": 3.1,
        }
        _print_nutrition(food_name, nutrition)
        return nutrition

    url = (
        f"http://openapi.foodsafetykorea.go.kr/api/{api_key}"
        f"/I2790/json/1/5/FOOD_NM_KR={food_name}"
    )
    try:
        res  = requests.get(url, timeout=5)
        rows = res.json().get("I2790", {}).get("row", [])

        if not rows:
            print(f"  ⚠️  '{food_name}' 검색 결과 없음")
            print("  → 식약처 DB에 없는 음식이거나 음식명 표기가 다를 수 있어요")
            return None

        row = rows[0]
        nutrition = {
            "calories":      float(row.get("AMT_NUM1")  or 0),
            "protein":       float(row.get("AMT_NUM3")  or 0),
            "fat":           float(row.get("AMT_NUM4")  or 0),
            "saturated_fat": float(row.get("AMT_NUM5")  or 0),
            "fiber":         float(row.get("AMT_NUM8")  or 0),
            "carbs":         float(row.get("AMT_NUM7")  or 0),
            "sugar":         float(row.get("AMT_NUM9")  or 0),
            "sodium":        float(row.get("AMT_NUM10") or 0),
        }
        print(f"  ✅ API 응답 성공!")
        _print_nutrition(food_name, nutrition)
        return nutrition

    except requests.exceptions.ConnectionError:
        print("  ❌ 네트워크 연결 실패")
        return None
    except Exception as e:
        print(f"  ❌ 오류: {e}")
        return None


def _print_nutrition(food_name: str, n: dict):
    print(f"\n  ┌─ {food_name} 영양 정보 (100g 기준) ─")
    print(f"  │  칼로리    {n['calories']:>7.1f} kcal")
    print(f"  │  탄수화물  {n['carbs']:>7.1f} g")
    print(f"  │  당류      {n['sugar']:>7.1f} g")
    print(f"  │  식이섬유  {n['fiber']:>7.1f} g")
    print(f"  │  단백질    {n['protein']:>7.1f} g")
    print(f"  │  지방      {n['fat']:>7.1f} g")
    print(f"  │  포화지방  {n['saturated_fat']:>7.1f} g")
    print(f"  └  나트륨    {n['sodium']:>7.1f} mg")


# ────────────────────────────────────────────
# 3. SQLite 저장 테스트
# ────────────────────────────────────────────
def test_db(food_name: str, nutrition: dict):
    print("\n" + "=" * 40)
    print("[ 3단계 ] SQLite DB 저장 테스트")
    print("=" * 40)

    db_path = "test_nutrition.db"
    conn    = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS nutrition (
            food_name     TEXT PRIMARY KEY,
            calories      REAL, protein      REAL, fat          REAL,
            saturated_fat REAL, fiber        REAL, carbs        REAL,
            sugar         REAL, sodium       REAL
        )
    """)
    conn.execute("""
        INSERT OR REPLACE INTO nutrition VALUES (?,?,?,?,?,?,?,?,?)
    """, (food_name, nutrition["calories"], nutrition["protein"],
          nutrition["fat"], nutrition["saturated_fat"], nutrition["fiber"],
          nutrition["carbs"], nutrition["sugar"], nutrition["sodium"]))
    conn.commit()

    row = conn.execute(
        "SELECT * FROM nutrition WHERE food_name=?", (food_name,)
    ).fetchone()
    conn.close()
    os.remove(db_path)   # 테스트용이므로 삭제

    if row:
        print(f"  ✅ 저장 및 조회 성공! → {row[0]}: {row[1]} kcal")
    else:
        print("  ❌ DB 저장 실패")


# ────────────────────────────────────────────
# 메인
# ────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="음식 칼로리 앱 CLI 테스트")
    parser.add_argument("--image",  default=None,   help="테스트할 음식 사진 경로")
    parser.add_argument("--apikey", default="DEMO", help="식약처 오픈API 키")
    args = parser.parse_args()

    print("\n🍱 음식 칼로리 앱 — CLI 동작 확인")
    print("  모델·API·DB 세 단계를 순서대로 테스트합니다.\n")

    food_name = test_model(args.image)
    nutrition = test_api(food_name, args.apikey)

    if nutrition:
        test_db(food_name, nutrition)

    print("\n" + "=" * 40)
    print("✅ 전체 흐름 확인 완료!")
    print("  문제 없으면 → streamlit run app.py 로 웹앱 실행")
    print("=" * 40 + "\n")


if __name__ == "__main__":
    main()
