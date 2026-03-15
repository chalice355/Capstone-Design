import streamlit as st
from PIL import Image

from model.predict import predict_spirit
from data.cocktail_db import get_cocktails_by_spirit, get_cocktail_detail

st.set_page_config(page_title="칵테일 레시피 추천", page_icon="🍸", layout="centered")

st.title("🍸 AI 칵테일 레시피 추천")
st.caption("주류 사진을 업로드하면 AI가 종류를 인식하고 만들 수 있는 칵테일을 추천해요.")

# --- 사진 업로드 ---
uploaded = st.file_uploader("주류 사진 업로드", type=["jpg", "jpeg", "png"])

if uploaded:
    image = Image.open(uploaded).convert("RGB")
    st.image(image, caption="업로드된 사진", use_column_width=True)

    with st.spinner("주류 인식 중..."):
        spirit_name, confidence = predict_spirit(image)

    st.success(f"**{spirit_name}** 으로 인식했어요! (신뢰도: {confidence:.1%})")

    # --- 칵테일 리스트 ---
    cocktails = get_cocktails_by_spirit(spirit_name)

    if cocktails:
        st.subheader(f"🍹 {spirit_name} 베이스 칵테일 {len(cocktails)}종")

        cols = st.columns(3)
        for i, cocktail in enumerate(cocktails):
            with cols[i % 3]:
                if st.button(cocktail["name"], key=f"btn_{i}", use_container_width=True):
                    st.session_state.selected = cocktail["cocktail_id"]

        # --- 레시피 상세 ---
        if "selected" in st.session_state:
            detail = get_cocktail_detail(st.session_state.selected)
            if detail:
                st.divider()
                st.subheader(f"🍸 {detail['name']}")

                st.markdown(f"> {detail['description']}")

                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**재료**")
                    for ing in detail["ingredients"]:
                        st.markdown(f"- {ing['measure']} {ing['ingredient']}")
                with col2:
                    if detail.get("thumbnail_url"):
                        st.image(detail["thumbnail_url"], use_column_width=True)

                st.markdown("**만드는 법**")
                st.info(detail["instructions"])
    else:
        st.warning("해당 주류로 만들 수 있는 칵테일 정보를 찾을 수 없어요.")

# --- 오늘의 랜덤 추천 ---
st.divider()
if st.button("🎲 오늘의 칵테일 랜덤 추천"):
    from data.cocktail_db import get_random_cocktail
    random = get_random_cocktail()
    if random:
        st.subheader(f"🍸 {random['name']}")
        st.markdown(f"> {random['description']}")
        if random.get("thumbnail_url"):
            st.image(random["thumbnail_url"], width=300)
