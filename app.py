import re
import streamlit as st

from database import (
    create_tables,
    create_user,
    get_user_by_email,
    verify_password,
    get_profiles
)


# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="LoveConnect — L'amour n'a pas de frontières",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

create_tables()


# =========================================================
# SESSION
# =========================================================

defaults = {
    "logged_in": False,
    "user_id": None,
    "user_name": None,
    "user_email": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# DESIGN PREMIUM
# =========================================================

st.markdown("""
<style>

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    visibility: hidden;
}

.stApp {
    background:
        radial-gradient(circle at 10% 10%, rgba(255, 220, 230, .75), transparent 28%),
        radial-gradient(circle at 90% 15%, rgba(255, 235, 240, .8), transparent 25%),
        linear-gradient(135deg, #fff8fa 0%, #ffffff 48%, #fff3f6 100%);
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* LOGO */

.logo {
    text-align: center;
    font-size: 42px;
    font-weight: 900;
    letter-spacing: -1px;
    color: #b3134f;
    margin-bottom: 0;
}

.tagline {
    text-align: center;
    color: #777;
    font-size: 15px;
    margin-bottom: 30px;
}


/* HERO */

.hero {
    padding: 55px 35px;
    border-radius: 30px;
    background:
        linear-gradient(
            135deg,
            rgba(255,255,255,.96),
            rgba(255,242,246,.96)
        );
    border: 1px solid rgba(179,19,79,.08);
    box-shadow: 0 20px 60px rgba(110,20,55,.10);
    text-align: center;
    margin-bottom: 30px;
}

.hero h1 {
    font-size: 46px;
    font-weight: 900;
    color: #222;
    margin-bottom: 12px;
}

.hero p {
    font-size: 19px;
    color: #666;
    max-width: 700px;
    margin: auto;
    line-height: 1.7;
}


/* SECTION */

.section-title {
    font-size: 30px;
    font-weight: 850;
    color: #222;
    margin-top: 25px;
    margin-bottom: 8px;
}

.section-subtitle {
    color: #777;
    margin-bottom: 25px;
}


/* PROFILE CARD */

.profile-card {
    background: rgba(255,255,255,.97);
    border: 1px solid rgba(179,19,79,.08);
    border-radius: 24px;
    padding: 24px;
    margin-bottom: 22px;
    box-shadow: 0 12px 35px rgba(0,0,0,.07);
    min-height: 260px;
}

.profile-avatar {
    width: 82px;
    height: 82px;
    border-radius: 50%;
    background: linear-gradient(135deg, #b3134f, #e85b8b);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 34px;
    font-weight: 800;
    margin-bottom: 15px;
}

.profile-name {
    font-size: 24px;
    font-weight: 800;
    color: #222;
}

.profile-age {
    color: #777;
    font-weight: 500;
}

.profile-location {
    color: #666;
    margin: 8px 0;
}

.profile-looking {
    color: #b3134f;
    font-weight: 650;
}

.profile-bio {
    color: #666;
    line-height: 1.6;
    margin-top: 12px;
}

.verified {
    display: inline-block;
    background: #eef9f1;
    color: #23753a;
    border-radius: 20px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 700;
}


/* DASHBOARD */

.dashboard {
    background: white;
    padding: 24px;
    border-radius: 22px;
    box-shadow: 0 10px 30px rgba(0,0,0,.06);
    margin-bottom: 25px;
}


/* WARNING */

.security {
    background: #fff8e8;
    border-left: 5px solid #e1a400;
    padding: 18px;
    border-radius: 14px;
    margin-top: 35px;
    color: #5c490
