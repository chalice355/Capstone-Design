import sys
import os
from pathlib import Path
from datetime import date

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# Django 초기화 (Streamlit 재실행 시 중복 방지)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "food_story.settings")
from django.apps import apps as django_apps
if not django_apps.ready:
    import django
    django.setup()

import streamlit as st
from PIL import Image
from story.services.llm_service import get_all_tabs
from story.services.wiki_service import search_origin
from model.predict import predict
from story.models import Diary

# ─── 페이지 설정 ──────────────────────────────────────────────────────────────

st.set_page_config(page_title="Food Story", page_icon="🍽️", layout="wide")

# ─── 세션 초기화 ──────────────────────────────────────────────────────────────

def _init():
    defaults = {
        "page":      "home",   # home | story | diary_save | diary_saved
        "food_name": None,
        "tabs_data": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ─── 네비게이션 헬퍼 ──────────────────────────────────────────────────────────

def _go(page, **kwargs):
    st.session_state.page = page
    for k, v in kwargs.items():
        st.session_state[k] = v
    st.rerun()

# ─── 공통 헤더 ────────────────────────────────────────────────────────────────

def _header(subtitle=""):
    st.markdown("# 🍽️ Food Story")
    if subtitle:
        st.caption(subtitle)
    st.divider()

# ─── 음식 정보 로드 ───────────────────────────────────────────────────────────

def _load_story(food_name: str) -> dict:
    wiki_text = search_origin(food_name)
    tabs_data = get_all_tabs(food_name)
    if wiki_text and "유래" in tabs_data:
        tabs_data["유래"] = wiki_text[:300] + "\n\n" + tabs_data["유래"]
    return tabs_data

# ─── PAGE: HOME ───────────────────────────────────────────────────────────────

def render_home():
    _header("음식의 유래, 어울리는 술, 이야기, 노래, 미디어를 알아보세요.")

    tab_search, tab_upload, tab_diary = st.tabs(
        ["🔍 음식 검색", "📷 사진 업로드", "📖 작성한 일기 보기"]
    )

    # ── 음식 검색 ──
    with tab_search:
        st.subheader("음식 이름으로 검색")
        food_input = st.text_input(
            "음식 이름", placeholder="예: 비빔밥", label_visibility="collapsed"
        )
        if st.button("검색 →", type="primary", use_container_width=True):
            if food_input.strip():
                with st.spinner(f"'{food_input.strip()}' 정보 불러오는 중..."):
                    tabs_data = _load_story(food_input.strip())
                _go("story", food_name=food_input.strip(), tabs_data=tabs_data)
            else:
                st.warning("음식 이름을 입력해주세요.")

    # ── 사진 업로드 ──
    with tab_upload:
        st.subheader("음식 사진으로 검색")
        uploaded = st.file_uploader(
            "사진 업로드", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
        )
        if uploaded:
            image = Image.open(uploaded).convert("RGB")
            col_img, col_info = st.columns([1, 1])
            with col_img:
                st.image(image, width=260)
            with col_info:
                with st.spinner("음식 인식 중..."):
                    result = predict(image)
                food_name = result["food_name"]
                if result.get("is_dummy"):
                    st.info(f"인식된 음식: **{food_name}**")
                else:
                    st.success(f"인식된 음식: **{food_name}** (신뢰도: {result['confidence']:.1%})")
                if st.button("이 음식으로 검색 →", type="primary", use_container_width=True):
                    with st.spinner(f"'{food_name}' 정보 불러오는 중..."):
                        tabs_data = _load_story(food_name)
                    _go("story", food_name=food_name, tabs_data=tabs_data)

    # ── 일기 목록 ──
    with tab_diary:
        st.subheader("작성한 일기 목록")
        diaries = list(Diary.objects.all())
        if not diaries:
            st.info("아직 작성된 일기가 없어요. 음식을 검색하고 일기를 남겨보세요!")
        else:
            for d in diaries:
                place_label = d.place if d.place else "장소 없음"
                with st.expander(f"📅 {d.date}  ·  🍽️ {d.food_name}  ·  📍 {place_label}"):
                    tab_labels = ["유래", "술", "이야기", "노래", "미디어"]
                    inner_tabs = st.tabs(tab_labels)
                    for inner_tab, key in zip(inner_tabs, tab_labels):
                        with inner_tab:
                            content = d.tabs_json.get(key, "내용 없음")
                            if key == "미디어" and isinstance(content, list):
                                for item in content:
                                    st.markdown(f"**{item['title']}**")
                                    st.write(item["description"])
                                    st.markdown(f"[바로가기]({item['link']})")
                                    st.divider()
                            else:
                                st.write(content)

# ─── PAGE: STORY ──────────────────────────────────────────────────────────────

def render_story():
    food_name = st.session_state.food_name
    tabs_data = st.session_state.tabs_data

    col_back, col_title = st.columns([1, 6])
    with col_back:
        if st.button("← 뒤로"):
            _go("home")
    with col_title:
        st.markdown(f"# 🍽️ {food_name}")
    st.divider()

    tab_labels = ["유래", "술", "이야기", "노래", "미디어"]
    tabs = st.tabs(tab_labels)

    for tab, key in zip(tabs, tab_labels):
        with tab:
            content = tabs_data.get(key, "정보를 불러오지 못했어요.")
            if key == "미디어" and isinstance(content, list):
                for item in content:
                    st.markdown(f"**{item['title']}**")
                    st.write(item["description"])
                    st.markdown(f"[바로가기]({item['link']})")
                    st.divider()
            else:
                st.write(content)

    st.divider()
    if st.button("📝 일기에 저장하기", type="primary"):
        _go("diary_save")

# ─── PAGE: DIARY SAVE ─────────────────────────────────────────────────────────

def render_diary_save():
    _header("일기 저장")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("날짜", value=str(date.today()), disabled=True)
    with col2:
        st.text_input("음식", value=st.session_state.food_name, disabled=True)

    place = st.text_input("장소", placeholder="예: 서울 종로구 인사동")
    st.divider()

    col_yes, col_no = st.columns(2)
    with col_yes:
        if st.button("💾 저장", type="primary", use_container_width=True):
            Diary.objects.create(
                food_name=st.session_state.food_name,
                place=place,
                date=date.today(),
                tabs_json=st.session_state.tabs_data,
            )
            _go("diary_saved")
    with col_no:
        if st.button("✕ 취소", use_container_width=True):
            _go("story")

# ─── PAGE: DIARY SAVED ────────────────────────────────────────────────────────

def render_diary_saved():
    st.markdown("## ✅ 일기가 저장되었습니다!")
    st.divider()
    st.write("첫 화면으로 돌아가시겠습니까?")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Yes, 홈으로", type="primary", use_container_width=True):
            _go("home", food_name=None, tabs_data=None)
    with col2:
        if st.button("📖 No, 계속 보기", use_container_width=True):
            _go("story")

# ─── 라우터 ───────────────────────────────────────────────────────────────────

PAGE_MAP = {
    "home":         render_home,
    "story":        render_story,
    "diary_save":   render_diary_save,
    "diary_saved":  render_diary_saved,
}

PAGE_MAP.get(st.session_state.page, render_home)()
