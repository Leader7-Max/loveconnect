import html
import re
import streamlit as st

from database import (
    create_tables,
    create_user,
    get_matches,
    get_messages,
    get_profiles,
    get_user_by_email,
    send_like,
    send_message,
    verify_password,
)

# Configuration de la page
st.set_page_config(
    page_title="LoveConnect",
    page_icon="❤️",
    layout="wide"
)

# Initialisation de la base de données (tables & colonnes)
create_tables()

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
defaults = {
    "logged_in": False,
    "user_id": None,
    "user_email": None,
    "registration_step": 1,
    "registration": {},
    "active_chat_user_id": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ---------------------------------------------------------
# STYLES & DESIGN (CSS)
# ---------------------------------------------------------
st.markdown("""
<style>  
#MainMenu, header, footer { visibility: hidden; }  
  
.stApp {  
    background: linear-gradient(135deg, #fff7fa, #ffffff, #fff1f6);  
}  
  
.block-container {  
    max-width: 1100px;  
    padding-top: 2rem;  
}  
  
.logo {  
    text-align: center;  
    color: #b3134f;  
    font-size: 42px;  
    font-weight: 900;  
}  
  
.tag {  
    text-align: center;  
    color: #777;  
    margin-bottom: 30px;  
}  
  
.hero, .card {  
    background: white;  
    border-radius: 24px;  
    padding: 28px;  
    box-shadow: 0 10px 35px rgba(0,0,0,.07);  
    margin-bottom: 20px;  
    border: 1px solid #f3dce5;  
}  
  
.avatar {  
    width: 70px;  
    height: 70px;  
    border-radius: 50%;  
    background: linear-gradient(135deg, #b3134f, #e85b8b);  
    color: white;  
    display: flex;  
    align-items: center;  
    justify-content: center;  
    font-size: 28px;  
    font-weight: bold;  
    margin-bottom: 10px;  
}  
  
.name { font-size: 23px; font-weight: 800; }  
.location { color: #666; margin-top: 8px; }  
.looking { color: #b3134f; font-weight: bold; margin-top: 8px; }  
.bio { color: #555; line-height: 1.6; margin-top: 12px; }  

div.stButton > button {
    border-radius: 12px;
    background-color: #b3134f;
    color: white;
    border: none;
}
</style>  
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# EN-TÊTE
# ---------------------------------------------------------
st.markdown('<div class="logo">❤️ LoveConnect</div>', unsafe_allow_html=True)
st.markdown('<div class="tag">L’amour n’a pas de frontières · Europe → Monde 🌍</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# ESPACE MEMBRE CONNECTÉ
# ---------------------------------------------------------
if st.session_state.logged_in:
    user = get_user_by_email(st.session_state.user_email)  

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

    # --- 1. MON PROFIL ---
    with tab_profile:  
        st.subheader("👤 Mon profil")  
        bio = user["bio"] or "Aucune présentation pour le moment."  
        initial = str(user["first_name"])[0].upper() if user["first_name"] else "?"  

        st.markdown(f"""  
        <div class="card">  
            <div class="avatar">{html.escape(initial)}</div>  
            <div class="name">{html.escape(str(user["first_name"]))} · {user["age"]} ans</div>  
            <div class="location">🌍 {html.escape(str(user["country"]))} · 📍 {html.escape(str(user["city"]))}</div>  
            <div class="looking">❤️ Recherche : {html.escape(str(user["looking_for"]))}</div>  
            <div class="bio"><strong>À propos de moi</strong><br><br>{html.escape(str(bio))}</div>  
        </div>  
        """, unsafe_allow_html=True)  

    # --- 2. DÉCOUVRIR ---
    with tab_discover:  
        st.subheader("💞 Découvrir")  
        st.write("Découvrez des personnes qui recherchent une relation sincère.")  

        country_search = st.text_input("🌍 Rechercher par pays", placeholder="France, Suisse, Cameroun...")  
        profiles = get_profiles(user["id"], country_search.strip())  

        if not profiles:  
            st.info("🌍 Aucun autre profil trouvé.")  
        else:  
            cols = st.columns(2)  
            for i, profile in enumerate(profiles):  
                with cols[i % 2]:  
                    first = str(profile["first_name"])  
                    bio = profile["bio"] or "Cette personne n’a pas encore ajouté de présentation."  
                    initial = first[0].upper() if first else "?"  

                    st.markdown(f"""  
                    <div class="card">  
                        <div class="avatar">{html.escape(initial)}</div>  
                        <div class="name">{html.escape(first)} · {profile["age"]} ans</div>  
                        <div class="location">🌍 {html.escape(str(profile["country"]))} · 📍 {html.escape(str(profile["city"]))}</div>  
                        <div class="looking">❤️ Recherche : {html.escape(str(profile["looking_for"]))}</div>  
                        <div class="bio">{html.escape(str(bio))}</div>  
                    </div>  
                    """, unsafe_allow_html=True)  

                    if st.button("❤️ Envoyez un coup de cœur", key=f"like_{profile['id']}", use_container_width=True):  
                        success, is_match = send_like(user["id"], profile["id"])
                        if success:
                            if is_match:
                                st.balloons()
                                st.success(f"💖 C'est un MATCH avec {first} ! Vous pouvez désormais discuter ensemble.")
                            else:
                                st.toast(f"❤️ Intérêt envoyé à {first} !")
                        else:
                            st.info(f"Vous avez déjà envoyé un coup de cœur à {first}.")

    # --- 3. MESSAGERIE ---
    with tab_messages:
        st.subheader("💬 Vos Conversations")
        matches = get_matches(user["id"])

        if not matches:
            st.info("Vous n'avez pas encore de match mutuel. Continuez à explorer des profils dans l'onglet 'Découvrir' !")
        else:
            col_list, col_chat = st.columns([1, 2])

            with col_list:
                st.write("**Vos matchs :**")
                for match in matches:
                    btn_label = f"💬 {match['first_name']} ({match['city']})"
                    if st.button(btn_label, key=f"chat_user_{match['id']}", use_container_width=True):
                        st.session_state.active_chat_user_id = match["id"]
                        st.rerun()

            with col_chat:
                active_id = st.session_state.active_chat_user_id
                
                # Sélectionner le premier match par défaut si aucun n'est actif
                if active_id is None and matches:
                    active_id = matches[0]["id"]
                    st.session_state.active_chat_user_id = active_id

                active_match = next((m for m in matches if m["id"] == active_id), None)

                if active_match:
                    st.markdown(f"### Discussion avec {active_match['first_name']}")
                    
                    # Récupération de l'historique
                    messages = get_messages(user["id"], active_match["id"])

                    chat_container = st.container(height=350)
                    with chat_container:
                        if not messages:
                            st.caption("C'est le début de votre histoire ! Envoyez le premier message.")
                        for msg in messages:
                            role = "user" if msg["sender_id"] == user["id"] else "assistant"
                            name = "Moi" if role == "user" else active_match["first_name"]
                            with st.chat_message(role):
                                st.write(f"**{name}** : {msg['content']}")

                    # Zone de saisie
                    new_msg = st.chat_input("Écrivez votre message...")
                    if new_msg:
                        if send_message(user["id"], active_match["id"], new_msg):
                            st.rerun()

# ---------------------------------------------------------
# ESPACE VISITEUR (INSCRIPTION / CONNEXION)
# ---------------------------------------------------------
else:
    st.markdown("""  
    <div class="hero">  
        <h1>Rencontrez quelqu’un de vrai. ❤️</h1>  
        <p>LoveConnect rapproche les personnes qui recherchent une relation sérieuse, sincère et fondée sur le respect.</p>  
        <p>🌍 De l’Europe au monde entier</p>  
    </div>  
    """, unsafe_allow_html=True)  

    tab_register, tab_login = st.tabs(["❤️ Créer mon profil", "🔐 Se connecter"])  

    # --- INSCRIPTION ---
    with tab_register:  
        step = st.session_state.registration_step  
        data = st.session_state.registration  

        st.caption(f"Étape {step} sur 3")  
        st.progress(step / 3)  

        # ÉTAPE 1
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

        # ÉTAPE 2
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

        # ÉTAPE 3
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
                    success, message = create_user(  
                        data["first_name"], data["age"], data["gender"], data["looking_for"],  
                        data["country"], data["city"], email_clean, phone.strip(), password, data["bio"]  
                    )  
                    if success:  
                        new_user = get_user_by_email(email_clean)  
                        if new_user:  
                            st.session_state.logged_in = True  
                            st.session_state.user_id = new_user["id"]  
                            st.session_state.user_email = email_clean  
                            st.session_state.registration = {}  
                            st.session_state.registration_step = 1  
                            st.rerun()  
                    else:  
                        st.error(f"❌ {message}")  

    # --- CONNEXION ---
    with tab_login:  
        st.header("🔐 Se connecter")  
        login_email = st.text_input("Adresse e-mail", key="login_email")  
        login_password = st.text_input("Mot de passe", type="password", key="login_password")  

        if st.button("🔐 Se connecter", use_container_width=True):  
            email_clean = login_email.strip().lower()  
            if not email_clean or not login_password:  
                st.error("Veuillez remplir tous les champs.")  
            else:  
                user = get_user_by_email(email_clean)  
                if user and verify_password(login_password, user["password"]):  
                    st.session_state.logged_in = True  
                    st.session_state.user_id = user["id"]  
                    st.session_state.user_email = email_clean  
                    st.rerun()  
                else:  
                    st.error("❌ E-mail ou mot de passe incorrect.")
  
