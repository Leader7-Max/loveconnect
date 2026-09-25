import streamlit as st
import re

from database import (
    create_tables,
    create_user,
    get_user_by_email,
    verify_password
)


# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="LoveConnect — L'amour n'a pas de frontières",
    page_icon="❤️",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =========================================================
# BASE DE DONNÉES
# =========================================================

create_tables()


# =========================================================
# SESSION
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None


# =========================================================
# STYLE
# =========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #fff7f8 0%,
        #ffffff 50%,
        #fff0f3 100%
    );
}

.main-title {
    text-align: center;
    font-size: 48px;
    font-weight: 800;
    margin-top: 35px;
    color: #b3124a;
}

.subtitle {
    text-align: center;
    font-size: 20px;
    color: #555;
    margin-bottom: 30px;
}

.hero {
    text-align: center;
    padding: 35px 20px;
    border-radius: 25px;
    background: rgba(255,255,255,0.9);
    box-shadow: 0 10px 35px rgba(0,0,0,0.08);
    margin-bottom: 30px;
}

.hero-title {
    font-size: 30px;
    font-weight: 700;
    color: #222;
}

.hero-text {
    font-size: 18px;
    line-height: 1.6;
    color: #555;
}

.warning {
    background: #fff8e8;
    border-left: 5px solid #e0a100;
    padding: 18px;
    border-radius: 12px;
    margin-top: 30px;
    color: #5f4b00;
}

.footer {
    text-align: center;
    color: #777;
    font-size: 13px;
    margin-top: 45px;
    padding-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# TITRE
# =========================================================

st.markdown(
    '<div class="main-title">❤️ LoveConnect</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">L’amour n’a pas de frontières 🌍</div>',
    unsafe_allow_html=True
)


# =========================================================
# UTILISATEUR CONNECTÉ
# =========================================================

if st.session_state.logged_in:

    st.success(
        f"❤️ Bienvenue {st.session_state.user_name} !"
    )

    st.markdown("""
    <div class="hero">

    <div class="hero-title">
    Votre espace LoveConnect
    </div>

    <p class="hero-text">
    Votre profil est maintenant connecté.
    </p>

    </div>
    """, unsafe_allow_html=True)

    if st.button(
        "🚪 Se
