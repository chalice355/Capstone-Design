import io
import random
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from server.model.predict import predict
from server.services.llm_service import get_tab_content, get_all_tabs
from server.services.wiki_service import search_origin

app = FastAPI(title="Food Story API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

FOOD_LIST = [
    "비빔밥", "된장찌개", "김치찌개", "삼겹살", "불고기",
    "떡볶이", "냉면", "설렁탕", "갈비탕", "순두부찌개",
    "잡채", "김밥", "도토리묵", "해물파전", "닭갈비",
    "갈비", "육개장", "보쌈", "족발", "순대",
]


@app.get("/")
def root():
    return {"status": "ok", "message": "Food Story API 서버가 실행 중입니다."}


@app.post("/predict")
async def predict_food(file: UploadFile = File(...)):
    """음식 사진 → 음식명 + 신뢰도 반환"""
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="이미지 파일만 업로드 가능해요.")

    contents = await file.read()
    image    = Image.open(io.BytesIO(contents)).convert("RGB")
    result   = predict(image)
    return result


@app.get("/story/{food_name}")
def get_story(food_name: str):
    """음식명 → 모든 탭 콘텐츠 반환"""
    wiki_text = search_origin(food_name)
    tabs      = get_all_tabs(food_name)

    if wiki_text and "유래" in tabs:
        tabs["유래"] = wiki_text[:300] + "\n\n" + tabs["유래"]

    return {"food_name": food_name, "tabs": tabs}


@app.get("/story/{food_name}/{tab}")
def get_story_tab(food_name: str, tab: str):
    """음식명 + 탭 이름 → 해당 탭 콘텐츠만 반환"""
    valid_tabs = ["유래", "술", "이야기", "노래", "미디어"]
    if tab not in valid_tabs:
        raise HTTPException(status_code=400, detail=f"탭은 {valid_tabs} 중 하나여야 해요.")

    if tab == "유래":
        wiki = search_origin(food_name)
        content = wiki[:300] if wiki else get_tab_content(food_name, tab)
    else:
        content = get_tab_content(food_name, tab)

    return {"food_name": food_name, "tab": tab, "content": content}


@app.get("/random")
def get_random_food():
    """랜덤 음식 반환"""
    food = random.choice(FOOD_LIST)
    return {"food_name": food}
