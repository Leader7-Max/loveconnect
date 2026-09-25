import html
import re
import streamlit as st
from streamlit_autorefresh import st_autorefresh

import database as db

st.set_page_config(
    page_title="LoveConnect",
    page_icon="❤️",
    layout="wide"
)

db.create_tables()

# Auto-refresh toutes les 3 secondes pour les notifications et messages en direct
st_autorefresh(interval=3000, key="datarefresh")

defaults = {
    "logged_in": False,
    "user_id": None,
    "user_email": None,
    "registration_step": 1,
    "registration": {},
    "active_chat_user_id": None,
    "liked_profiles": set(),
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown("""
<style>  
#MainMenu, header, footer { visibility: hidden; }  
  
.stApp {  
    background: linear-gradient(135deg, #f8f9fa, #ffffff, #fff0f5);  
}  
  
.block-container {  
    max-width: 1000px;  
    padding-top: 2rem;  
}  
  
.logo {  
    text-align: center;  
    color: #e63946;  
    font-size: 38px;  
    font-weight: 900;  
    letter-spacing: -1px;
}  
  
.tag {  
    text-align: center;  
    color: #6c757d;  
    margin-bottom: 35px;  
    font-size: 15px;
}  

.profile-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(230, 57, 70, 0.08);
    text-align: center;
    margin-bottom: 15px;
    border: 1px solid #fdf0f3;
}

.profile-avatar {
    width: 90px;
    height: 90px;
    border-radius: 50%;
    background: linear-gradient(135deg, #e63946, #ff6b6b);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    font-weight: bold;
    margin: 0 auto 16px auto;
    box-shadow: 0 4px 15px rgba(230, 57, 70, 0.2);
}

.profile-name { font-size: 22px; font-weight: 800; color: #1d3557; }
.profile-location { color: #457b9d; font-size: 14px; font-weight: 500; margin: 6px 0; }
.profile-bio { 
    color: #495057; 
    font-size: 15px; 
    line-height: 1.5; 
    margin-top: 16px; 
    padding-top: 16px; 
    border-top: 1px solid #f1f3f5; 
    font-style: italic;
}

div.stButton > button {
    border-radius: 12px;
    background-color: #e63946;
    color: white;
    border: none;
    font-weight: 600;
    padding: 10px 0;
}
div.stButton > button:hover {
    background-color: #d62828;
    color: white;
}
div.stButton > button:disabled {
    background-color: #e9ecef;
    color: #adb5bd;
}
</style>  
""", unsafe_allow_html=True)

st.markdown('<div class="logo">❤️ LoveConnect</div>', unsafe_allow_html=True)
st.markdown('<div class="tag">L’amour n’a pas de frontières · Europe → Monde 🌍</div>', unsafe_allow_html=True)

if st.session_state.logged_in:
    user = db.get_user_by_email(st.session_state.user_email)  

    if user is None:  
        st.session_state.logged_in = False  
        st.rerun()  

    col1, col2 = st.columns([4, 1])  

    with col1:  
        st.success(f"❤️ Bonjour {user['first_name']}, bienvenue sur LoveConnect.")  

    with col2:  
        if st.button("🚪 Déconnexion", use_container_width=True):  
            st.session_state.logged_in = False  
            st.session_state.user_id = None  
            st.session_state.user_email = None  
            st.session_state.active_chat_user_id = None
            st.rerun()  

    tab_profile, tab_discover, tab_messages = st.tabs([
        "👤 Mon profil", 
        "💞 Découvrir", 
        "💬 Messagerie"
    ])  

    with tab_profile:  
        st.subheader("👤 Mon profil")  
        bio = user["bio"] or "Aucune présentation pour le moment."  
        initial = str(user["first_name"])[0].upper() if user["first_name"] else "?"  

        st.markdown(f"""  
        <div class="profile-card">  
            <div class="profile-avatar">{html.escape(initial)}</div>  
            <div class="profile-name">{html.escape(str(user["first_name"]))}, {user["age"]} ans</div>  
            <div class="profile-location">🌍 {html.escape(str(user["country"]))} · 📍 {html.escape(str(user["city"]))}</div>  
            <div class="profile-bio"><strong>À propos de moi</strong><br><br>{html.escape(str(bio))}</div>  
        </div>  
        """, unsafe_allow_html=True)  

    with tab_discover:  
        st.subheader("💞 Découvrir")  
        country_search = st.text_input("🌍 Filtrer par pays", placeholder="Ex: France, Suisse, Cameroun...")  
        profiles = db.get_profiles(user["id"], country_search.strip())  

        if not profiles:  
            st.info("🌍 Aucun autre profil trouvé dans cette zone.")  
        else:  
            cols = st.columns(2)  
            for i, profile in enumerate(profiles):  
                with cols[i % 2]:  
                    first = str(profile["first_name"])  
                    bio = profile["bio"] or "Aucune présentation renseignée."  
                    initial = first[0].upper() if first else "?"  

                    st.markdown(f"""  
                    <div class="profile-card">  
                        <div class="profile-avatar">{html.escape(initial)}</div>  
                        <div class="profile-name">{html.escape(first)}, {profile["age"]} ans</div>  
                        <div class="profile-location">🌍 {html.escape(str(profile["country"]))} · 📍 {html.escape(str(profile["city"]))}</div>  
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
                                    st.success(f"🎉 MATCH avec {first} !")
                                else:
                                    st.toast(f"❤️ Intérêt envoyé à {first} !")
                            st.rerun()

    with tab_messages:
        st.subheader("💬 Vos Conversations")
        matches = db.get_matches(user["id"])

        if not matches:
            st.info("Vous n'avez pas encore de match mutuel. Continuez à explorer des profils dans l'onglet 'Découvrir' !")
        else:
            match_options = {f"💬 {m['first_name']} ({m['city']})": m["id"] for m in matches}
            selected_label = st.selectbox("Sélectionnez une discussion :", list(match_options.keys()))
            
            active_id = match_options[selected_label]
            active_match = next((m for m in matches if m["id"] == active_id), None)

            if active_match:
                st.markdown(f"### Discussion avec {active_match['first_name']}")
                messages = db.get_messages(user["id"], active_match["id"])

                chat_container = st.container(height=400)
                with chat_container:
                    if not messages:
                        st.caption("C'est le début de votre histoire ! Envoyez le premier message.")
                    for msg in messages:
                        is_me = (msg["sender_id"] == user["id"])
                        avatar = "👤" if is_me else "💖"
                        role = "user" if is_me else "assistant"
                        with st.chat_message(role, avatar=avatar):
                            name = "Moi" if is_me else active_match["first_name"]
                            st.write(f"**{name}** : {msg['content']}")

                new_msg = st.chat_input("Écrivez votre message...")
                if new_msg:
                    if db.send_message(user["id"], active_match["id"], new_msg):
                        st.rerun()

else:
    st.markdown("""  
    <div class="profile-card">  
        <h1>Rencontrez quelqu’un de vrai. ❤️</h1>  
        <p>LoveConnect rapproche les personnes qui recherchent une relation sérieuse, sincère et fondée sur le respect.</p>  
        <p>🌍 De l’Europe au monde entier</p>  
    </div>  
    """, unsafe_allow_html=True)  

    tab_register, tab_login = st.tabs(["❤️ Créer mon profil", "🔐 Se connecter"])  

    with tab_register:  
        step = st.session_state.registration_step  
        data = st.session_state.registration  

        st.caption(f"Étape {step} sur 3")  
        st.progress(step / 3)  

        if step == 1:  
            st.header("👤 Qui êtes-vous ?")  
            with st.form("step1"):  
                first_name = st.text_input("Prénom", value=data.get("first_name", ""), placeholder="Exemple : Pavel")  
                age = st.number_input("Âge", min_value=18, max_value=100, value=int(data.get("age", 18)))  
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
            st.header("❤️ Que recherchez-vous ?")  
            with st.form("step2"):  
                options = ["Une femme", "Un homme", "Une personne"]  
                looking_for = st.selectbox("Je recherche", options, index=options.index(data.get("looking_for", "Une personne")))  
                country = st.text_input("🌍 Pays", value=data.get("country", ""), placeholder="France")  
                city = st.text_input("📍 Ville", value=data.get("city", ""), placeholder="Lyon")  
                bio = st.text_area("💬 Votre bio", value=data.get("bio", ""), max_chars=600, height=140)  
                
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
                elif len(bio.strip()) < 20:  
                    st.error("Votre bio doit contenir au moins 20 caractères.")  
                else:  
                    data.update({"looking_for": looking_for, "country": country.strip(), "city": city.strip(), "bio": bio.strip()})  
                    st.session_state.registration = data  
                    st.session_state.registration_step = 3  
                    st.rerun()  

        else:  
            st.header("🔐 Créez votre compte")  
            with st.form("step3"):  
                email = st.text_input("📧 Adresse e-mail", value=data.get("email", ""), placeholder="vous@example.com")  
                phone = st.text_input("📱 Téléphone (optionnel)", value=data.get("phone", ""), placeholder="+33...")  
                password = st.text_input("🔑 Mot de passe", type="password")  
                password_confirm = st.text_input("🔑 Confirmer le mot de passe", type="password")  
                accept = st.checkbox("Je confirme avoir 18 ans ou plus et accepter les conditions.")  

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
                    st.error("Le mot de passe doit contenir au moins 6 caractères.")  
                elif password != password_confirm:  
                    st.error("Les mots de passe ne correspondent pas.")  
                elif not accept:  
                    st.error("Vous devez accepter les conditions.")  
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
        st.header("🔐 Se connecter")  
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
