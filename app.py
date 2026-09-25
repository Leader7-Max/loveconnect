import re
import streamlit as st

from database import (
    create_tables,
    create_user,
    get_user_by_email,
    verify_password,
    get_profiles
)

st.set_page_config(
    page_title="LoveConnect",
    page_icon="❤️",
    layout="wide"
)

create_tables()

# =========================
# SESSION
# =========================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None


# =========================
# DESIGN
# =========================

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
        radial-gradient(
            circle at 10% 10%,
            rgba(255,210,225,.7),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 10%,
            rgba(255,230,240,.8),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            #fff8fa,
            #ffffff,
            #fff2f6
        );
}

.block-container {
    max-width: 1150px;
    padding-top: 2rem;
}

.logo {
    text-align: center;
    color: #b3134f;
    font-size: 42px;
    font-weight: 900;
}

.tagline {
    text-align: center;
    color: #777;
    margin-bottom: 30px;
}

.hero {
    background: white;
    border-radius: 30px;
    padding: 45px 25px;
    text-align: center;
    box-shadow: 0 15px 50px rgba(0,0,0,.08);
    margin-bottom: 30px;
}

.hero h1 {
    font-size: 42px;
    color: #222;
}

.hero p {
    color: #666;
    font-size: 18px;
    line-height: 1.6;
}

.dashboard {
    background: white;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 8px 25px rgba(0,0,0,.06);
    margin-bottom: 25px;
}

.profile-card {
    background: white;
    border-radius: 24px;
    padding: 25px;
    margin-bottom: 10px;
    box-shadow: 0 10px 30px rgba(0,0,0,.07);
    border: 1px solid #f4dce5;
}

.avatar {
    width: 75px;
    height: 75px;
    border-radius: 50%;
    background: linear-gradient(
        135deg,
        #b3134f,
        #e85b8b
    );
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    font-weight: bold;
    margin-bottom: 12px;
}

.profile-name {
    font-size: 24px;
    font-weight: 800;
    color: #222;
}

.profile-age {
    color: #777;
    font-size: 17px;
}

.profile-location {
    color: #666;
    margin-top: 8px;
}

.profile-looking {
    color: #b3134f;
    font-weight: bold;
    margin-top: 8px;
}

.profile-bio {
    color: #555;
    line-height: 1.6;
    margin-top: 14px;
}

.verified {
    display: inline-block;
    background: #edf9f0;
    color: #26763d;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: bold;
    margin-top: 8px;
}

.security {
    background: #fff8e8;
    border-left: 5px solid #e0a100;
    border-radius: 12px;
    padding: 18px;
    margin-top: 35px;
    color: #5d4b00;
}

.footer {
    text-align: center;
    color: #888;
    padding: 40px 0 15px;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# =========================
# LOGO
# =========================

st.markdown(
    '<div class="logo">❤️ LoveConnect</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="tagline">'
    'L’amour n’a pas de frontières · Europe → Monde 🌍'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# UTILISATEUR CONNECTÉ
# =========================================================

if st.session_state.logged_in:

    user = get_user_by_email(
        st.session_state.user_email
    )

    if user:

        # =========================
        # BARRE DU COMPTE
        # =========================

        col1, col2 = st.columns([4, 1])

        with col1:

            st.markdown(
                f"""
                <div class="dashboard">
                ❤️ <strong>Bonjour {user["first_name"]}</strong><br>
                <span style="color:#777;">
                Bienvenue sur LoveConnect.
                </span>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col2:

            if st.button(
                "🚪 Déconnexion",
                use_container_width=True
            ):

                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.session_state.user_email = None

                st.rerun()


        # =========================
        # NAVIGATION
        # =========================

        profil_tab, discover_tab = st.tabs(
            [
                "👤 Mon profil",
                "💞 Découvrir"
            ]
        )


        # =================================================
        # MON PROFIL
        # =================================================

        with profil_tab:

            st.subheader("👤 Mon profil")

            first_letter = (
                user["first_name"][0].upper()
                if user["first_name"]
                else "?"
            )

            bio = user["bio"] or (
                "Aucune présentation pour le moment."
            )

            st.markdown(
                f"""
                <div class="profile-card">

                <div class="avatar">
                {first_letter}
                </div>

                <div class="profile-name">
                {user["first_name"]}
                <span class="profile-age">
                · {user["age"]} ans
                </span>
                </div>

                <div class="profile-location">
                🌍 {user["country"]}
                · 📍 {user["city"]}
                </div>

                <div class="profile-looking">
                ❤️ Recherche : {user["looking_for"]}
                </div>

                <div class="profile-bio">
                <strong>À propos de moi</strong><br><br>
                {bio}
                </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            if user["verified"]:

                st.success("🛡️ Profil vérifié")

            else:

                st.info(
                    "⏳ Vérification du profil prochainement."
                )


        # =================================================
        # DÉCOUVRIR
        # =================================================

        with discover_tab:

            st.subheader("💞 Découvrir")

            st.write(
                "Découvrez des personnes qui recherchent "
                "une relation sincère."
            )

            search_country = st.text_input(
                "🌍 Rechercher par pays",
                placeholder="France, Suisse, Cameroun...",
                key="country_search"
            )

            profiles = get_profiles(
                user["id"],
                search_country.strip()
            )

            if not profiles:

                st.info(
                    "🌍 Aucun autre profil trouvé."
                )

                st.caption(
                    "Crée un deuxième faux profil pour tester "
                    "cette section."
                )

            else:

                columns = st.columns(2)

                for index, profile in enumerate(profiles):

                    with columns[index % 2]:

                        first_letter = (
                            profile["first_name"][0].upper()
                            if profile["first_name"]
                            else "?"
                        )

                        bio = profile["bio"] or (
                            "Cette personne n'a pas encore "
                            "ajouté de présentation."
                        )

                        st.markdown(
                            f"""
                            <div class="profile-card">

                            <div class="avatar">
                            {first_letter}
                            </div>

                            <div class="profile-name">
                            {profile["first_name"]}
                            <span class="profile-age">
                            · {profile["age"]} ans
                            </span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        if profile["verified"]:

                            st.markdown(
                                '<div class="verified">'
                                '✓ Profil vérifié'
                                '</div>',
                                unsafe_allow_html=True
                            )

                        st.markdown(
                            f"""
                            <div class="profile-location">
                            🌍 {profile["country"]}
                            · 📍 {profile["city"]}
                            </div>

                            <div class="profile-looking">
                            ❤️ Recherche :
                            {profile["looking_for"]}
                            </div>

                            <div class="profile-bio">
                            {bio}
                            </div>

                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        like_col, interest_col = st.columns(2)

                        with like_col:

                            if st.button(
                                "❤️ J'aime",
                                key=f"like_{profile['id']}",
                                use_container_width=True
                            ):

                                st.toast(
                                    f"❤️ Intérêt envoyé à "
                                    f"{profile['first_name']} !"
                                )

                        with interest_col:

                            if st.button(
                                "💌 Intéressé(e)",
                                key=f"interest_{profile['id']}",
                                use_container_width=True
                            ):

                                st.toast(
                                    f"💌 Intérêt envoyé à "
                                    f"{profile['first_name']}."
                                )


# =========================================================
# VISITEUR
# =========================================================

else:

    st.markdown(
        """
        <div class="hero">

        <h1>Rencontrez quelqu’un de vrai. ❤️</h1>

        <p>
        LoveConnect rapproche les personnes qui recherchent
        une relation sérieuse, sincère et fondée sur le respect.
        </p>

        <p>
        🌍 De l’Europe au monde entier
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    inscription_tab, connexion_tab = st.tabs(
        [
            "❤️ Créer mon profil",
            "🔐 Se connecter"
        ]
    )


    # =====================================================
    # INSCRIPTION
    # =====================================================

    with inscription_tab:

        st.subheader("❤️ Créer votre profil")

        st.info(
            "🔞 LoveConnect est réservé aux personnes "
            "âgées de 18 ans ou plus."
        )

        with st.form("registration_form"):

            first_name = st.text_input("Prénom")

            age = st.number_input(
                "Âge",
                min_value=18,
                max_value=100,
                value=18
            )

            gender = st.selectbox(
                "Je suis",
                ["Homme", "Femme", "Autre"]
            )

            looking_for = st.selectbox(
                "Je recherche",
                [
                    "Une femme",
                    "Un homme",
                    "Une personne"
                ]
            )

            country = st.text_input(
                "Pays",
                placeholder="France"
            )

            city = st.text_input(
                "Ville",
                placeholder="Lyon"
            )

            email = st.text_input(
                "Adresse e-mail"
            )

            phone = st.text_input(
                "Téléphone (optionnel)"
            )

            password = st.text_input(
                "Mot de passe",
                type="password"
            )

            bio = st.text_area(
                "Présentez-vous",
                placeholder=(
                    "Parlez de vous, de vos passions "
                    "et de ce que vous recherchez..."
                )
            )

            accept = st.checkbox(
                "Je confirme avoir 18 ans ou plus "
                "et accepter les règles de LoveConnect."
            )

            submit = st.form_submit_button(
                "❤️ Créer mon profil",
                use_container_width=True
            )


        if submit:

            email_clean = email.strip().lower()

            if not first_name.strip():

                st.error("Veuillez entrer votre prénom.")

            elif not country.strip():

                st.error("Veuillez entrer votre pays.")

            elif not city.strip():

                st.error("Veuillez entrer votre ville.")

            elif not re.match(
                r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
                email_clean
            ):

                st.error(
                    "Veuillez entrer une adresse e-mail valide."
                )

            elif len(password) < 6:

                st.error(
                    "Le mot de passe doit contenir "
                    "au moins 6 caractères."
                )

            elif not accept:

                st.error(
                    "Vous devez confirmer avoir 18 ans ou plus."
                )

            else:

                success, message = create_user(
                    first_name.strip(),
                    int(age),
                    gender,
                    looking_for,
                    country.strip(),
                    city.strip(),
                    email_clean,
                    phone.strip(),
                    password,
                    bio.strip()
                )

                if success:

                    st.success(
                        "🎉 " + message
                    )

                    st.info(
                        "Vous pouvez maintenant vous connecter."
                    )

                else:

                    st.error(
                        "❌ " + message
                    )


    # =====================================================
    # CONNEXION
    # =====================================================

    with connexion_tab:

        st.subheader("🔐 Se connecter")

        login_email = st.text_input(
            "Adresse e-mail",
            key="login_email"
        )

        login_password = st.text_input(
            "Mot de passe",
            type="password",
            key="login_password"
        )

        login = st.button(
            "🔐 Se connecter",
            use_container_width=True
        )

        if login:

            email_clean = login_email.strip().lower()

            if not email_clean or not login_password:

                st.error(
                    "Veuillez entrer votre e-mail "
                    "et votre mot de passe."
                )

            else:

                user = get_user_by_email(
                    email_clean
                )

                if user is None:

                    st.error(
                        "❌ E-mail ou mot de passe incorrect."
                    )

                else:

                    password_valid = verify_password(
                        login_password,
                        user["password"]
                    )

                    if password_valid:

                        st.session_state.logged_in = True
                        st.session_state.user_id = user["id"]
                        st.session_state.user_name = user["first_name"]
                        st.session_state.user_email = email_clean

                        st.rerun()

                    else:

                        st.error(
                            "❌ E-mail ou mot de passe incorrect."
                        )


# =========================================================
# MESSAGE DE SÉCURITÉ
# =========================================================

st.markdown(
    """
    <div class="security">

    <strong>🛡️ Votre sécurité avant tout</strong><br><br>

    Ne partagez jamais vos informations bancaires,
    mots de passe ou documents personnels avec une
    personne rencontrée en ligne.

    Méfiez-vous des demandes d'argent et signalez
    tout comportement suspect.

    Pour une première rencontre, privilégiez toujours
    un lieu public.

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">

    ❤️ <strong>LoveConnect</strong><br>

    Des rencontres sincères, au-delà des frontières 🌍<br><br>

    🔞 Plateforme réservée aux personnes majeures.

    </div>
    """,
    unsafe_allow_html=True
)
