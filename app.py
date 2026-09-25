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
    "liked_profiles": set(),
    "last_msg_count": 0
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def process_image(uploaded_file):
    if uploaded_file is None:
        return None
    try:
        img = Image.open(uploaded_file)
        img = img.convert("RGB")
        img.thumbnail((400, 400))
        buffer = BytesIO()
        img.save(buffer, format="JPEG", quality=80)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')
    except Exception:
        return None

def render_avatar(photo_b64, initial):
    if photo_b64:
        return f'<img src="data:image/jpeg;base64,{photo_b64}" class="profile-avatar-img" />'
    return f'<div class="profile-avatar-placeholder">{html.escape(initial)}</div>'

st.markdown("""
<style>  
#MainMenu, header, footer { visibility: hidden; }  
.stApp { background-color: #fafafa; }  
.block-container { max-width: 720px; padding-top: 1rem; padding-bottom: 2rem; }  
.logo { text-align: center; color: #e63946; font-size: 28px; font-weight: 900; }  
.tag { text-align: center; color: #6c757d; margin-bottom: 20px; font-size: 13px; }  

.profile-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    text-align: center;
    margin-bottom: 12px;
    border: 1px solid #f1f3f5;
}

.profile-avatar-img {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    object-fit: cover;
    margin: 0 auto 10px auto;
    border: 2px solid #e63946;
}

.profile-avatar-placeholder {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    background: linear-gradient(135deg, #e63946, #ff4d6d);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 32px;
    font-weight: bold;
    margin: 0 auto 10px auto;
}

.profile-name { font-size: 18px; font-weight: 700; color: #212529; }
.profile-location { color: #6c757d; font-size: 12px; margin: 2px 0; }
.profile-bio { color: #495057; font-size: 13.5px; line-height: 1.4; margin-top: 10px; padding-top: 10px; border-top: 1px solid #f8f9fa; }

div.stButton > button {
    border-radius: 10px;
    background-color: #e63946;
    color: white;
    border: none;
    font-weight: 600;
}
</style>  
""", unsafe_allow_html=True)

st.markdown('<div class="logo">❤️ LoveConnect</div>', unsafe_allow_html=True)
st.markdown('<div class="tag">Rencontres sérieuses & authentiques 🌍</div>', unsafe_allow_html=True)

if st.session_state.logged_in:
    raw_user = db.get_user_by_email(st.session_state.user_email)  

    if raw_user is None:  
        st.session_state.logged_in = False  
        st.rerun()  

    user = dict(raw_user)
    
    if hasattr(db, "update_last_seen"):
        db.update_last_seen(user["id"])

    matches = [dict(m) for m in db.get_matches(user["id"])]
    
    total_messages_received = 0
    if matches:
        for m in matches:
            msgs = db.get_messages(user["id"], m["id"])
            for msg in msgs:
                if dict(msg)["sender_id"] != user["id"]:
                    total_messages_received += 1

    if total_messages_received > st.session_state.last_msg_count:
        if st.session_state.last_msg_count != 0:
            components.html("""
                <script>
                    var ctx = new (window.AudioContext || window.webkitAudioContext)();
                    var osc = ctx.createOscillator();
                    var gain = ctx.createGain();
                    osc.type = 'sine';
                    osc.frequency.value = 587.33;
                    gain.gain.setValueAtTime(0.1, ctx.currentTime);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start();
                    osc.stop(ctx.currentTime + 0.2);
                </script>
            """, height=0)
        st.session_state.last_msg_count = total_messages_received

    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.write(f"Bonjour **{user['first_name']}** 👋")
    with col_head2:
        if st.button("Déconnexion", key="btn_logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.rerun()

    tab_profile, tab_discover, tab_messages = st.tabs([
        "👤 Mon profil", 
        "💞 Découvrir", 
        "💬 Messagerie"
    ])  

    with tab_profile:  
        bio = user.get("bio") or "Aucune présentation."  
        initial = str(user["first_name"])[0].upper() if user.get("first_name") else "?"  
        avatar_html = render_avatar(user.get("photo"), initial)
        status_html = db.format_last_seen(user.get("last_seen")) if hasattr(db, "format_last_seen") else ""

        st.markdown(f"""  
        <div class="profile-card">  
            {avatar_html}
            <div>{status_html}</div>
            <div class="profile-name">{html.escape(str(user["first_name"]))}, {user["age"]} ans</div>  
            <div class="profile-location">🌍 {html.escape(str(user["country"]))} · 📍 {html.escape(str(user["city"]))}</div>  
            <div class="profile-bio">{html.escape(str(bio))}</div>  
        </div>  
        """, unsafe_allow_html=True)  

        new_photo = st.file_uploader("Modifier ma photo de profil", type=["jpg", "jpeg", "png"])
        if new_photo:
            photo_b64 = process_image(new_photo)
            if photo_b64:
                db.update_user_photo(user["id"], photo_b64)
                st.success("Photo de profil mise à jour !")
                st.rerun()

    with tab_discover:  
        country_search = st.text_input("🌍 Filtrer par pays", placeholder="France, Suisse, Cameroun...")  
        raw_profiles = db.get_profiles(user["id"], country_search.strip())  

        if not raw_profiles:  
            st.info("Aucun autre profil disponible pour le moment.")  
        else:  
            cols = st.columns(2)  
            for i, raw_profile in enumerate(raw_profiles):  
                profile = dict(raw_profile)
                with cols[i % 2]:  
                    first = str(profile["first_name"])  
                    bio = profile.get("bio") or "Aucune présentation."  
                    initial = first[0].upper() if first else "?"  
                    avatar_html = render_avatar(profile.get("photo"), initial)
                    status_html = db.format_last_seen(profile.get("last_seen")) if hasattr(db, "format_last_seen") else ""

                    st.markdown(f"""  
                    <div class="profile-card">  
                        {avatar_html}
                        <div>{status_html}</div>
                        <div class="profile-name">{html.escape(first)}, {profile["age"]} ans</div>  
                        <div class="profile-location">📍 {html.escape(str(profile["city"]))}, {html.escape(str(profile["country"]))}</div>  
                        <div class="profile-bio">"{html.escape(str(bio))}"</div>  
                    </div>  
                    """, unsafe_allow_html=True)  

                    if profile['id'] in st.session_state.liked_profiles:
                        st.button("💖 Coup de cœur envoyé", key=f"liked_{profile['id']}", disabled=True, use_container_width=True)
                    else:
                        if st.button("❤️ Coup de cœur", key=f"like_{profile['id']}", use_container_width=True):  
                            success, is_match = db.send_like(user["id"], profile["id"])
                            st.session_state.liked_profiles.add(profile['id']) 
                            if success:
                                if is_match:
                                    st.balloons()
                                    st.success(f"🎉 C'est un MATCH avec {first} !")
                                else:
                                    st.toast(f"❤️ Coup de cœur envoyé à {first} !")
                            st.rerun()

    with tab_messages:
        if not matches:
            st.info("Vous n'avez pas encore de conversation en cours.")
        else:
            if st.session_state.active_chat_user_id is None:
                st.session_state.active_chat_user_id = matches[0]['id']

            m_cols = st.columns(len(matches))
            for idx, m in enumerate(matches):
                with m_cols[idx]:
                    is_active = (m['id'] == st.session_state.active_chat_user_id)
                    btn_style = f"🟢 {m['first_name']}" if is_active else f"💬 {m['first_name']}"
                    if st.button(btn_style, key=f"chat_tab_{m['id']}", use_container_width=True):
                        st.session_state.active_chat_user_id = m['id']
                        st.rerun()

            st.divider()

            active_match = next((m for m in matches if m["id"] == st.session_state.active_chat_user_id), matches[0])
            active_status = db.format_last_seen(active_match.get("last_seen")) if hasattr(db, "format_last_seen") else ""

            st.caption(f"Discussion avec **{active_match['first_name']}** ({active_match['city']}) — {active_status}", unsafe_allow_html=True)
            raw_messages = db.get_messages(user["id"], active_match["id"])

            chat_container = st.container(height=360)
            with chat_container:
                if not raw_messages:
                    st.caption("Écrivez le premier message !")
                for raw_msg in raw_messages:
                    msg = dict(raw_msg)
                    is_me = (msg["sender_id"] == user["id"])
                    avatar = "👤" if is_me else "💖"
                    role = "user" if is_me else "assistant"
                    with st.chat_message(role, avatar=avatar):
                        st.write(msg['content'])

            new_msg = st.chat_input("Écrivez un message...")
            if new_msg:
                if db.send_message(user["id"], active_match["id"], new_msg):
                    st.rerun()

else:
    st.markdown("""  
    <div class="profile-card">  
        <h3>Rencontrez quelqu’un de vrai ❤️</h3>  
        <p>LoveConnect rapproche les personnes qui recherchent une relation sérieuse, sincère et durable.</p>  
    </div>  
    """, unsafe_allow_html=True)  

    tab_register, tab_login = st.tabs(["❤️ Créer un profil", "🔐 Se connecter"])  

    with tab_register:  
        step = st.session_state.registration_step  
        data = st.session_state.registration  

        st.caption(f"Étape {step} sur 3")  
        st.progress(step / 3)  

        if step == 1:  
            st.subheader("👤 Qui êtes-vous ?")  
            with st.form("step1"):  
                first_name = st.text_input("Prénom", value=data.get("first_name", ""), placeholder="Ex: Pavel")  
                age = st.number_input("Âge", min_value=18, max_value=100, value=int(data.get("age", 25)))  
                genders = ["Homme", "Femme", "Autre"]  
                gender = st.selectbox("Je suis", genders, index=genders.index(data.get("gender", "Homme")))  
                
                photo_file = st.file_uploader("Photo de profil (optionnelle)", type=["jpg", "jpeg", "png"])
                
                if st.form_submit_button("Continuer →", use_container_width=True):  
                    if not first_name.strip():  
                        st.error("Veuillez entrer votre prénom.")  
                    else:  
                        photo_b64 = process_image(photo_file) if photo_file else None
                        data.update({
                            "first_name": first_name.strip(), 
                            "age": int(age), 
                            "gender": gender,
                            "photo": photo_b64
                        })  
                        st.session_state.registration = data  
                        st.session_state.registration_step = 2  
                        st.rerun()  

        elif step == 2:  
            st.subheader("❤️ Votre recherche")  
            with st.form("step2"):  
                options = ["Une femme", "Un homme", "Une personne"]  
                looking_for = st.selectbox("Je recherche", options, index=options.index(data.get("looking_for", "Une femme")))  
                country = st.text_input("🌍 Pays", value=data.get("country", ""), placeholder="France")  
                city = st.text_input("📍 Ville", value=data.get("city", ""), placeholder="Grenoble")  
                bio = st.text_area("💬 Présentation", value=data.get("bio", ""), max_chars=500, height=120)  
                
                col_back, col_next = st.columns(2)  
                with col_back:  
                    back = st.form_submit_button("← Retour", use_container_width=True)  
                with col_next:  
                    next_btn = st.form_submit_button("Continuer →", use_container_width=True)  

            if back:  
                st.session_state.registration_step = 1  
                st.rerun()  
            elif next_btn:  
                if not country.strip() or not city.strip():  
                    st.error("Veuillez indiquer votre pays et votre ville.")  
                elif len(bio.strip()) < 15:  
                    st.error("Présentez-vous en au moins 15 caractères.")  
                else:  
                    data.update({"looking_for": looking_for, "country": country.strip(), "city": city.strip(), "bio": bio.strip()})  
                    st.session_state.registration = data  
                    st.session_state.registration_step = 3  
                    st.rerun()  

        else:  
            st.subheader("🔐 Identifiants")  
            with st.form("step3"):  
                email = st.text_input("📧 Adresse e-mail", value=data.get("email", ""), placeholder="adresse@exemple.com")  
                phone = st.text_input("📱 Téléphone (optionnel)", value=data.get("phone", ""))  
                password = st.text_input("🔑 Mot de passe", type="password")  
                password_confirm = st.text_input("🔑 Confirmer le mot de passe", type="password")  
                accept = st.checkbox("J'ai au moins 18 ans et j'accepte les conditions d'utilisation.")  

                col_back, col_create = st.columns(2)  
                with col_back:  
                    back = st.form_submit_button("← Retour", use_container_width=True)  
                with col_create:  
                    create_btn = st.form_submit_button("❤️ Créer mon profil", use_container_width=True)  

            if back:  
                st.session_state.registration_step = 2  
                st.rerun()  
            elif create_btn:  
                email_clean = email.strip().lower()  
                if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email_clean):  
                    st.error("E-mail invalide.")  
                elif len(password) < 6:  
                    st.error("Le mot de passe doit comporter au moins 6 caractères.")  
                elif password != password_confirm:  
                    st.error("Les mots de passe ne correspondent pas.")  
                elif not accept:  
                    st.error("Vous devez valider les conditions.")  
                else:  
                    success, message = db.create_user(  
                        data["first_name"], data["age"], data["gender"], data["looking_for"],  
                        data["country"], data["city"], email_clean, phone.strip(), password, data["bio"],
                        data.get("photo")
                    )  
                    if success:  
                        raw_new_user = db.get_user_by_email(email_clean)  
                        if raw_new_user:  
                            st.session_state.logged_in = True  
                            st.session_state.user_id = raw_new_user["id"]  
                            st.session_state.user_email = email_clean  
                            st.session_state.registration = {}  
                            st.session_state.registration_step = 1  
                            st.rerun()  
                    else:  
                        st.error(f"❌ {message}")  

    with tab_login:  
        st.subheader("🔐 Connexion")  
        login_email = st.text_input("Adresse e-mail", key="login_email")  
        login_password = st.text_input("Mot de passe", type="password", key="login_password")  

        if st.button("🔐 Se connecter", use_container_width=True):  
            email_clean = login_email.strip().lower()  
            if not email_clean or not login_password:  
                st.error("Veuillez remplir tous les champs.")  
            else:  
                raw_user = db.get_user_by_email(email_clean)  
                if raw_user:  
                    user = dict(raw_user)  
                    if db.verify_password(login_password, user["password"]):  
                        st.session_state.logged_in = True  
                        st.session_state.user_id = user["id"]  
                        st.session_state.user_email = email_clean  
                        st.rerun()  
                    else:  
                        st.error("❌ E-mail ou mot de passe incorrect.")  
                else:  
                    st.error("❌ E-mail ou mot de passe incorrect.")
