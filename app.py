import html
import re
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

# Rafraîchissement automatique toutes les 3 secondes
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

# Style CSS Épuré & Premium Mobile-First
st.markdown("""
<style>  
#MainMenu, header, footer { visibility: hidden; }  
  
.stApp {  
    background-color: #fafafa;  
}  
  
.block-container {  
    max-width: 720px;  
    padding-top: 1rem;  
    padding-bottom: 2rem;
}  
  
.logo {  
    text-align: center;  
    color: #e63946;  
    font-size: 28px;  
    font-weight: 900;  
    letter-spacing: -0.5px;
}  
  
.tag {  
    text-align: center;  
    color: #6c757d;  
    margin-bottom: 20px;  
    font-size: 13px;
}  

/* Cartes Profil */
.profile-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 18px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    text-align: center;
    margin-bottom: 12px;
    border: 1px solid #f1f3f5;
}

.profile-avatar {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    background: linear-gradient(135deg, #e63946, #ff4d6d);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    font-weight: bold;
    margin: 0 auto 10px auto;
}

.profile-name { font-size: 18px; font-weight: 700; color: #212529; }
.profile-location { color: #6c757d; font-size: 12px; margin: 2px 0; }
.profile-bio { 
    color: #495057; 
    font-size: 13.5px; 
    line-height: 1.4; 
    margin-top: 10px; 
    padding-top: 10px; 
    border-top: 1px solid #f8f9fa; 
}

/* Éléments de bouton épurés */
div.stButton > button {
    border-radius: 10px;
    background-color: #e63946;
    color: white;
    border: none;
    font-weight: 600;
    padding: 8px 12px;
}
div.stButton > button:hover {
    background-color: #d62828;
    color: white;
}
</style>  
""", unsafe_allow_html=True)

st.markdown('<div class="logo">❤️ LoveConnect</div>', unsafe_allow_html=True)
st.markdown('<div class="tag">Rencontres sérieuses & authentiques 🌍</div>', unsafe_allow_html=True)

if st.session_state.logged_in:
    user = db.get_user_by_email(st.session_state.user_email)  

    if user is None:  
        st.session_state.logged_in = False  
        st.rerun()  

    matches = db.get_matches(user["id"])
    
    # Calcul des messages non lus
    unread_count = 0
    total_messages_received = 0
    if matches:
        for m in matches:
            msgs = db.get_messages(user["id"], m["id"])
            for msg in msgs:
                if msg["sender_id"] != user["id"]:
                    total_messages_received += 1

    # Jouer une tonalité audio si un nouveau message est reçu
    if total_messages_received > st.session_state.last_msg_count:
        if st.session_state.last_msg_count != 0:
            components.html("""
                <script>
                    var ctx = new (window.AudioContext || window.webkitAudioContext)();
                    var osc = ctx.createOscillator();
                    var gain = ctx.createGain();
                    osc.type = 'sine';
                    osc.frequency.value = 587.33; // D5
                    gain.gain.setValueAtTime(0.1, ctx.currentTime);
                    osc.connect(gain);
                    gain.connect(ctx.destination);
                    osc.start();
                    osc.stop(ctx.currentTime + 0.2);
                </script>
            """, height=0)
        st.session_state.last_msg_count = total_messages_received

    msg_tab_title = "💬 Messagerie"
    if unread_count > 0:
        msg_tab_title = f"💬 Messagerie ({unread_count})"

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
        msg_tab_title
    ])  

    with tab_profile:  
        bio = user["bio"] or "Aucune présentation pour le moment."  
        initial = str(user["first_name"])[0].upper() if user["first_name"] else "?"  

        st.markdown(f"""  
        <div class="profile-card">  
            <div class="profile-avatar">{html.escape(initial)}</div>  
            <div class="profile-name">{html.escape(str(user["first_name"]))}, {user["age"]} ans</div>  
            <div class="profile-location">🌍 {html.escape(str(user["country"]))} · 📍 {html.escape(str(user["city"]))}</div>  
            <div class="profile-bio">{html.escape(str(bio))}</div>  
        </div>  
        """, unsafe_allow_html=True)  

    with tab_discover:  
        country_search = st.text_input("🌍 Filtrer par pays", placeholder="France, Suisse, Cameroun...")  
        profiles = db.get_profiles(user["id"], country_search.strip())  

        if not profiles:  
            st.info("Aucun autre profil disponible pour le moment.")  
        else:  
            cols = st.columns(2)  
            for i, profile in enumerate(profiles):  
                with cols[i % 2]:  
                    first = str(profile["first_name"])  
                    bio = profile["bio"] or "Aucune présentation."  
                    initial = first[0].upper() if first else "?"  

                    st.markdown(f"""  
                    <div class="profile-card">  
                        <div class="profile-avatar">{html.escape(initial)}</div>  
                        <div class="profile-name">{html.escape(first)}, {profile["age"]} ans</div>  
                        <div class="profile-location">📍 {html.escape(str(profile["city"]))}, {html.escape(str(profile["country"]))}</div>  
                        <div class="profile-bio">"{html.escape(str(bio))}"</div>  
                    </div>  
                    """, unsafe_allow_html=True)  

                    if profile['id'] in st.session_state.liked_profiles:
                        st.button("💖 Coup de cœur envoyé", key=f"liked_{profile['id']}", disabled=True, use_container_width=True)
                    else:
                        if st.button("❤️ Envoyer un coup de cœur", key=f"like_{profile['id']}", use_container_width=True):  
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
            # Sélecteur horizontal de correspondants épuré
            if st.session_state.active_chat_user_id is None:
                st.session_state.active_chat_user_id = matches[0]['id']

            m_cols = st.columns(len(matches))
            for idx, m in enumerate(matches):
                with m_cols[idx]:
                    is_active = (m['id'] == st.session_state.active_chat_user_id)
                    btn_style = f"💬 {m['first_name']}"
                    if is_active:
                        btn_style = f"🟢 {m['first_name']}"
                    if st.button(btn_style, key=f"chat_tab_{m['id']}", use_container_width=True):
                        st.session_state.active_chat_user_id = m['id']
                        st.rerun()

            st.divider()

            active_match = next((m for m in matches if m["id"] == st.session_state.active_chat_user_id), matches[0])

            st.caption(f"Discussion avec **{active_match['first_name']}** ({active_match['city']})")
            messages = db.get_messages(user["id"], active_match["id"])

            chat_container = st.container(height=360)
            with chat_container:
                if not messages:
                    st.caption("Écrivez le premier message !")
                for msg in messages:
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
                
                if st.form_submit_button("Continuer →", use_container_width=True):  
                    if not first_name.strip():  
                        st.error("Veuillez entrer votre prénom.")  
                    else:  
                        data.update({"first_name": first_name.strip(), "age": int(age), "gender": gender})  
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
                        data["country"], data["city"], email_clean, phone.strip(), password, data["bio"]  
                    )  
                    if success:  
                        new_user = db.get_user_by_email(email_clean)  
                        if new_user:  
                            st.session_state.logged_in = True  
                            st.session_state.user_id = new_user["id"]  
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
                user = db.get_user_by_email(email_clean)  
                if user and db.verify_password(login_password, user["password"]):  
                    st.session_state.logged_in = True  
                    st.session_state.user_id = user["id"]  
                    st.session_state.user_email = email_clean  
                    st.rerun()  
                else:  
                    st.error("❌ E-mail ou mot de passe incorrect.")
          
