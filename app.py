import html
import re
import base64
from io import BytesIO
from PIL import Image
import streamlit as st
import streamlit.components.v1 as components
from streamlit_autorefresh import st_autorefresh

import database as db

st.set_page_config(
    page_title="LoveConnect",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

db.create_tables()

st_autorefresh(interval=3000, key="datarefresh")

defaults = {
    "logged_in": False,
    "user_id": None,
    "user_email": None,
    "registration_step": 1,
    "registration": {},
    "active_chat_user_id": None,
    "last_msg_count": 0,
    "respect_preferences": True,
    "confirm_delete_account": False,
    "confirm_unmatch": None,
    "report_target": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# ---------------------------------------------------------------------------
# Utilitaires
# ---------------------------------------------------------------------------

def process_image(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        img = Image.open(uploaded_file)
        img = img.convert("RGB")
        img.thumbnail((400, 400))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception:
        return None


def render_avatar(photo_b64, initial, size=90, online=False):
    ring = "avatar-ring-online" if online else ""
    if photo_b64:
        return f'<img src="data:image/jpeg;base64,{photo_b64}" class="profile-avatar-img {ring}" style="width:{size}px;height:{size}px;" />'
    return f'<div class="profile-avatar-placeholder {ring}" style="width:{size}px;height:{size}px;font-size:{int(size*0.36)}px;">{html.escape(initial)}</div>'


def play_notification_sound():
    components.html("""
        <script>
            var ctx = new (window.AudioContext || window.webkitAudioContext)();
            var osc = ctx.createOscillator();
            var gain = ctx.createGain();
            osc.type = 'sine';
            osc.frequency.value = 587.33;
            gain.gain.setValueAtTime(0.12, ctx.currentTime);
            osc.connect(gain);
            gain.connect(ctx.destination);
            osc.start();
            osc.stop(ctx.currentTime + 0.2);
        </script>
    """, height=0)


# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

#MainMenu, header, footer { visibility: hidden; }

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: radial-gradient(circle at 10% 0%, #fff0f3 0%, #fafafa 45%), #fafafa;
}

.block-container { max-width: 760px; padding-top: 1.2rem; padding-bottom: 2rem; }

.logo {
    text-align: center;
    font-family: 'Poppins', sans-serif;
    font-weight: 800;
    font-size: 32px;
    background: linear-gradient(90deg, #e63946, #ff4d6d, #ff758f);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.5px;
}
.tag { text-align: center; color: #94a3b8; margin-bottom: 22px; font-size: 13px; font-weight: 500; }

.profile-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 6px 20px rgba(230, 57, 70, 0.07);
    text-align: center;
    margin-bottom: 14px;
    border: 1px solid #f4f4f6;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.profile-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 26px rgba(230, 57, 70, 0.12);
}

.profile-avatar-img, .profile-avatar-placeholder {
    border-radius: 50%;
    object-fit: cover;
    margin: 0 auto 10px auto;
    display: flex;
    align-items: center;
    justify-content: center;
}
.profile-avatar-img { border: 3px solid #ffffff; box-shadow: 0 0 0 3px #ff4d6d; }
.profile-avatar-placeholder {
    background: linear-gradient(135deg, #e63946, #ff4d6d);
    color: white;
    font-weight: 700;
    box-shadow: 0 0 0 3px #ff4d6d;
}
.avatar-ring-online { box-shadow: 0 0 0 3px #16a34a !important; }

.profile-name { font-family: 'Poppins', sans-serif; font-size: 19px; font-weight: 700; color: #212529; margin-top: 4px; }
.profile-location { color: #94a3b8; font-size: 12.5px; margin: 3px 0; font-weight: 500; }
.profile-bio {
    color: #495057;
    font-size: 13.5px;
    line-height: 1.5;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px dashed #f1f3f5;
}

.badge-pill {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 999px;
    font-size: 11.5px;
    font-weight: 600;
    background: #fff0f3;
    color: #e63946;
    margin: 4px 2px;
}

.stat-box {
    background: linear-gradient(135deg, #ffffff, #fff5f6);
    border: 1px solid #ffe3e8;
    border-radius: 16px;
    padding: 14px 8px;
    text-align: center;
}
.stat-number { font-family: 'Poppins', sans-serif; font-size: 22px; font-weight: 800; color: #e63946; }
.stat-label { font-size: 11.5px; color: #94a3b8; font-weight: 600; text-transform: uppercase; letter-spacing: 0.4px; }

div.stButton > button, div.stFormSubmitButton > button {
    border-radius: 12px;
    background: linear-gradient(135deg, #e63946, #ff4d6d);
    color: white;
    border: none;
    font-weight: 600;
    transition: transform 0.1s ease, filter 0.1s ease;
}
div.stButton > button:hover, div.stFormSubmitButton > button:hover {
    filter: brightness(1.06);
    transform: translateY(-1px);
}
div.stButton > button:disabled {
    background: #f1f3f5;
    color: #adb5bd;
}

.pass-btn button {
    background: #f8f9fa !important;
    color: #495057 !important;
    border: 1px solid #e9ecef !important;
}

.danger-btn button {
    background: linear-gradient(135deg, #495057, #212529) !important;
}

.unread-dot {
    background: #e63946;
    color: white;
    border-radius: 999px;
    padding: 1px 7px;
    font-size: 11px;
    font-weight: 700;
    margin-left: 4px;
}

.section-title {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    color: #212529;
    font-size: 15px;
    margin: 6px 0 10px 0;
}

.empty-state {
    text-align: center;
    color: #94a3b8;
    padding: 30px 10px;
    font-size: 14px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="logo">❤️ LoveConnect</div>', unsafe_allow_html=True)
st.markdown('<div class="tag">Rencontres sérieuses & authentiques 🌍</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Application connectée
# ---------------------------------------------------------------------------

if st.session_state.logged_in:
    raw_user = db.get_user_by_email(st.session_state.user_email)

    if raw_user is None:
        st.session_state.logged_in = False
        st.rerun()

    user = dict(raw_user)
    db.update_last_seen(user["id"])

    matches = [dict(m) for m in db.get_matches(user["id"])]
    liked_me = [dict(p) for p in db.get_users_who_liked_me(user["id"])]
    total_unread = db.get_total_unread(user["id"])
    stats = db.get_stats(user["id"])

    if total_unread > st.session_state.last_msg_count:
        if st.session_state.last_msg_count != 0:
            play_notification_sound()
        st.session_state.last_msg_count = total_unread

    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.write(f"Bonjour **{user['first_name']}** 👋")
    with col_head2:
        if st.button("Déconnexion", key="btn_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.rerun()

    liked_badge = f" ({len(liked_me)})" if liked_me else ""
    msg_badge = f" ({total_unread})" if total_unread else ""

    tab_profile, tab_discover, tab_liked, tab_messages, tab_settings = st.tabs([
        "👤 Mon profil",
        "💞 Découvrir",
        f"✨ Qui m'a aimé{liked_badge}",
        f"💬 Messagerie{msg_badge}",
        "⚙️ Paramètres",
    ])

    # ------------------------------------------------------------------
    # Mon profil
    # ------------------------------------------------------------------
    with tab_profile:
        bio = user.get("bio") or "Aucune présentation."
        initial = str(user["first_name"])[0].upper() if user.get("first_name") else "?"
        avatar_html = render_avatar(user.get("photo"), initial, online=True)

        st.markdown(f"""
        <div class="profile-card">
            {avatar_html}
            <div class="profile-name">{html.escape(str(user["first_name"]))}, {user["age"]} ans</div>
            <div class="profile-location">🌍 {html.escape(str(user["country"]))} · 📍 {html.escape(str(user["city"]))}</div>
            <div class="badge-pill">Recherche : {html.escape(str(user["looking_for"]))}</div>
            <div class="profile-bio">{html.escape(str(bio))}</div>
        </div>
        """, unsafe_allow_html=True)

        s1, s2, s3 = st.columns(3)
        with s1:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["likes_sent"]}</div><div class="stat-label">Envoyés</div></div>', unsafe_allow_html=True)
        with s2:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["matches"]}</div><div class="stat-label">Matches</div></div>', unsafe_allow_html=True)
        with s3:
            st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["likes_received"]}</div><div class="stat-label">Reçus</div></div>', unsafe_allow_html=True)

        st.write("")
        new_photo = st.file_uploader("📷 Modifier ma photo de profil", type=["jpg", "jpeg", "png"])
        if new_photo:
            photo_b64 = process_image(new_photo)
            if photo_b64:
                db.update_user_photo(user["id"], photo_b64)
                st.success("Photo de profil mise à jour !")
                st.rerun()

        with st.expander("✏️ Modifier mes informations"):
            with st.form("edit_profile"):
                options_looking = ["Une femme", "Un homme", "Une personne"]
                edit_looking_for = st.selectbox(
                    "Je recherche", options_looking,
                    index=options_looking.index(user["looking_for"]) if user["looking_for"] in options_looking else 0
                )
                edit_country = st.text_input("🌍 Pays", value=user["country"])
                edit_city = st.text_input("📍 Ville", value=user["city"])
                edit_bio = st.text_area("💬 Présentation", value=user.get("bio") or "", max_chars=500, height=110)

                if st.form_submit_button("💾 Enregistrer", use_container_width=True):
                    if not edit_country.strip() or not edit_city.strip():
                        st.error("Le pays et la ville sont obligatoires.")
                    elif len(edit_bio.strip()) < 15:
                        st.error("Présentez-vous en au moins 15 caractères.")
                    else:
                        db.update_profile(user["id"], edit_bio.strip(), edit_country.strip(), edit_city.strip(), edit_looking_for)
                        st.success("Profil mis à jour !")
                        st.rerun()

    # ------------------------------------------------------------------
    # Découvrir
    # ------------------------------------------------------------------
    with tab_discover:
        with st.expander("🔎 Filtres de recherche", expanded=False):
            f1, f2 = st.columns(2)
            with f1:
                country_search = st.text_input("🌍 Pays", placeholder="France, Suisse, Cameroun...")
            with f2:
                city_search = st.text_input("📍 Ville", placeholder="Grenoble, Genève...")
            age_range = st.slider("🎂 Tranche d'âge", 18, 100, (18, 60))
            respect_pref = st.checkbox(
                "Respecter mes préférences de genre", value=st.session_state.respect_preferences
            )
            st.session_state.respect_preferences = respect_pref

        raw_profiles = db.get_profiles(
            user["id"],
            country_filter=country_search.strip() if country_search else "",
            city_filter=city_search.strip() if city_search else "",
            min_age=age_range[0],
            max_age=age_range[1],
            respect_preferences=st.session_state.respect_preferences,
        )

        if not raw_profiles:
            st.markdown('<div class="empty-state">💔 Aucun profil disponible avec ces filtres pour le moment.</div>', unsafe_allow_html=True)
        else:
            cols = st.columns(2)
            for i, raw_profile in enumerate(raw_profiles):
                profile = dict(raw_profile)
                with cols[i % 2]:
                    first = str(profile["first_name"])
                    bio = profile.get("bio") or "Aucune présentation."
                    initial = first[0].upper() if first else "?"
                    online = db.is_online(profile.get("last_seen"))
                    avatar_html = render_avatar(profile.get("photo"), initial, online=online)
                    status_html = db.format_last_seen(profile.get("last_seen"))

                    st.markdown(f"""
                    <div class="profile-card">
                        {avatar_html}
                        <div>{status_html}</div>
                        <div class="profile-name">{html.escape(first)}, {profile["age"]} ans</div>
                        <div class="profile-location">📍 {html.escape(str(profile["city"]))}, {html.escape(str(profile["country"]))}</div>
                        <div class="profile-bio">"{html.escape(str(bio))}"</div>
                    </div>
                    """, unsafe_allow_html=True)

                    b1, b2 = st.columns(2)
                    with b1:
                        st.markdown('<div class="pass-btn">', unsafe_allow_html=True)
                        if st.button("✖️ Passer", key=f"pass_{profile['id']}", use_container_width=True):
                            db.pass_profile(user["id"], profile["id"])
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    with b2:
                        if st.button("❤️ Coup de cœur", key=f"like_{profile['id']}", use_container_width=True):
                            success, is_match = db.send_like(user["id"], profile["id"])
                            if success:
                                if is_match:
                                    st.balloons()
                                    st.success(f"🎉 C'est un MATCH avec {first} !")
                                else:
                                    st.toast(f"❤️ Coup de cœur envoyé à {first} !")
                            st.rerun()

    # ------------------------------------------------------------------
    # Qui m'a aimé
    # ------------------------------------------------------------------
    with tab_liked:
        if not liked_me:
            st.markdown('<div class="empty-state">✨ Personne ne vous a encore envoyé de coup de cœur.<br>Continuez à découvrir des profils !</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="section-title">{len(liked_me)} personne(s) vous ont envoyé un coup de cœur 💌</div>', unsafe_allow_html=True)
            cols = st.columns(2)
            for i, profile in enumerate(liked_me):
                with cols[i % 2]:
                    first = str(profile["first_name"])
                    bio = profile.get("bio") or "Aucune présentation."
                    initial = first[0].upper() if first else "?"
                    online = db.is_online(profile.get("last_seen"))
                    avatar_html = render_avatar(profile.get("photo"), initial, online=online)

                    st.markdown(f"""
                    <div class="profile-card">
                        {avatar_html}
                        <div class="badge-pill">💌 Vous a aimé</div>
                        <div class="profile-name">{html.escape(first)}, {profile["age"]} ans</div>
                        <div class="profile-location">📍 {html.escape(str(profile["city"]))}, {html.escape(str(profile["country"]))}</div>
                        <div class="profile-bio">"{html.escape(str(bio))}"</div>
                    </div>
                    """, unsafe_allow_html=True)

                    b1, b2 = st.columns(2)
                    with b1:
                        st.markdown('<div class="pass-btn">', unsafe_allow_html=True)
                        if st.button("✖️ Ignorer", key=f"skip_liked_{profile['id']}", use_container_width=True):
                            db.pass_profile(user["id"], profile["id"])
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
                    with b2:
                        if st.button("❤️ Aimer en retour", key=f"likeback_{profile['id']}", use_container_width=True):
                            success, is_match = db.send_like(user["id"], profile["id"])
                            if success and is_match:
                                st.balloons()
                                st.success(f"🎉 C'est un MATCH avec {first} !")
                            st.rerun()

    # ------------------------------------------------------------------
    # Messagerie
    # ------------------------------------------------------------------
    with tab_messages:
        if not matches:
            st.markdown('<div class="empty-state">💬 Vous n\'avez pas encore de conversation.<br>Likez des profils pour créer un match !</div>', unsafe_allow_html=True)
        else:
            if st.session_state.active_chat_user_id not in [m["id"] for m in matches]:
                st.session_state.active_chat_user_id = matches[0]['id']

            m_cols = st.columns(len(matches))
            for idx, m in enumerate(matches):
                with m_cols[idx]:
                    is_active = (m['id'] == st.session_state.active_chat_user_id)
                    unread = db.get_unread_count(user["id"], m["id"])
                    label = f"🟢 {m['first_name']}" if is_active else f"💬 {m['first_name']}"
                    if unread:
                        label += f" ({unread})"
                    if st.button(label, key=f"chat_tab_{m['id']}", use_container_width=True):
                        st.session_state.active_chat_user_id = m['id']
                        st.rerun()

            st.divider()

            active_match = next((m for m in matches if m["id"] == st.session_state.active_chat_user_id), matches[0])
            db.mark_messages_read(user["id"], active_match["id"])
            active_status = db.format_last_seen(active_match.get("last_seen"))

            head_col1, head_col2 = st.columns([4, 1])
            with head_col1:
                st.markdown(
                    f"Discussion avec **{active_match['first_name']}** ({active_match['city']}) — {active_status}",
                    unsafe_allow_html=True
                )
            with head_col2:
                with st.popover("⋯", use_container_width=True):
                    if st.button("🚫 Ne plus matcher", key=f"unmatch_{active_match['id']}", use_container_width=True):
                        db.unmatch(user["id"], active_match["id"])
                        st.session_state.active_chat_user_id = None
                        st.success("Match retiré.")
                        st.rerun()
                    if st.button("⛔ Bloquer", key=f"block_{active_match['id']}", use_container_width=True):
                        db.block_user(user["id"], active_match["id"])
                        db.unmatch(user["id"], act
