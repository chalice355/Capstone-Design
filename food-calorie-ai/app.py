import streamlit as st
from PIL import Image
import torch
import pandas as pd
import plotly.express as px

from model.predict import predict_food
from data.nutrition_db import get_nutrition

st.set_page_config(page_title="칼로리 계산기", page_icon="🍱", layout="centered")

st.title("🍱 음식 사진 칼로리 계산기")
st.caption("사진을 업로드하면 AI가 음식을 인식하고 칼로리를 알려드려요.")

# --- 사진 업로드 ---
uploaded = st.file_uploader("음식 사진 업로드", type=["jpg", "jpeg", "png"])

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="업로드된 사진", use_column_width=True)

    with st.spinner("음식 인식 중..."):
        food_name, confidence = predict_food(image)

    st.success(f"**{food_name}** 으로 인식했어요! (신뢰도: {confidence:.1%})")

    nutrition = get_nutrition(food_name)

    if nutrition:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("칼로리", f"{nutrition['calories']} kcal")
        col2.metric("탄수화물", f"{nutrition['carbs']} g")
        col3.metric("단백질", f"{nutrition['protein']} g")
        col4.metric("지방", f"{nutrition['fat']} g")

        # 영양소 비율 파이 차트
        fig = px.pie(
            values=[nutrition['carbs'], nutrition['protein'], nutrition['fat']],
            names=["탄수화물", "단백질", "지방"],
            title="영양소 비율",
            color_discrete_sequence=["#7F77DD", "#1D9E75", "#EF9F27"],
        )
        st.plotly_chart(fig, use_container_width=True)

        # 식단 기록 저장
        if "records" not in st.session_state:
            st.session_state.records = []

        if st.button("식단에 추가하기"):
            st.session_state.records.append({
                "음식": food_name,
                "칼로리": nutrition["calories"],
                "탄수화물": nutrition["carbs"],
                "단백질": nutrition["protein"],
                "지방": nutrition["fat"],
            })
            st.toast(f"{food_name} 기록 완료!")

    else:
        st.warning("영양 정보를 찾을 수 없어요. DB에 없는 음식일 수 있어요.")

# --- 오늘의 식단 기록 ---
if "records" in st.session_state and st.session_state.records:
    st.divider()
    st.subheader("📋 오늘의 식단 기록")
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df, use_container_width=True)
    total = df["칼로리"].sum()
    st.metric("오늘 총 칼로리", f"{total} kcal")

    fig2 = px.bar(df, x="음식", y="칼로리", title="음식별 칼로리",
                  color_discrete_sequence=["#7F77DD"])
    st.plotly_chart(fig2, use_container_width=True)
