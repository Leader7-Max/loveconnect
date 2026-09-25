import html
import re

import streamlit as st

from database import (
    create_tables,
    create_user,
    get_profiles,
    get_user_by_email,
    verify_password,
)


# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="LoveConnect",
    page_icon="❤️",
    layout="wide",
)

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

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "registration_step" not in st.session_state:
    st.session_state.registration_step = 1

if "registration" not in st.session_state:
    st.session_state.registration = {}


# =========================================================
# STYLE
# =========================================================

st.markdown(
    """
    <style>

    #MainMenu {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 10% 10%,
                rgba(255, 210, 225, 0.70),
                transparent 30%
            ),
            radial-gradient(
                circle at 90% 10%,
                rgba(255, 230, 240, 0.80),
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
        padding-bottom: 3rem;
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
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.08);
        margin-bottom: 30px;
        border: 1px solid #f5dce5;
    }

    .hero h1 {
        color: #222;
        font-size: 42px;
    }

    .hero p {
        color: #666;
        font-size: 18px;
        line-height: 1.6;
    }

    .step-card {
        background: white;
        border-radius: 25px;
        padding: 30px;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.07);
        border: 1px solid #f2dce5;
        margin-bottom: 20px;
    }

    .step-title {
        color: #b3134f;
        font-size: 27px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .step-description {
        color: #777;
        line-height: 1.6;
    }

    .step-number {
        text-align: center;
        color: #b3134f;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .dashboard {
        background: white;
        border-radius: 20px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.06);
        margin-bottom: 25px;
    }

    .profile-card {
        background: white;
        border-radius: 24px;
        padding: 25px;
        margin-bottom: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.07);
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
    """,
    unsafe_allow_html=True,
)


# =========================================================
# LOGO
# =========================================================

st.markdown(
    '<div class="logo">❤️ LoveConnect</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="tagline">'
    "L’amour n’a pas de frontières · Europe → Monde 🌍"
    "</div>",
    unsafe_allow_html=True,
)


# =========================================================
# UTILISATEUR CONNECTÉ
# =========================================================

if st.session_state.logged_in:

    user = get_user_by_email(
        st.session_state.user_email
    )

    if user is None:

        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.user_email = None

        st.rerun()

    # -----------------------------------------------------
    # COMPTE
    # -----------------------------------------------------

    col_account, col_logout = st.columns([4, 1])

    with col_account:

        safe_name = html.escape(
            str(user["first_name"])
        )

        st.markdown(
            f"""
            <div class="dashboard">
                ❤️ <strong>Bonjour {safe_name}</strong><br>
                <span style="color:#777;">
                    Bienvenue sur LoveConnect.
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_logout:

        if st.button(
            "🚪 Déconnexion",
            use_container_width=True,
        ):

            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.session_state.user_email = None

            st.rerun()

    # -----------------------------------------------------
    # NAVIGATION
    # -----------------------------------------------------

    profile_tab, discover_tab = st.tabs(
        [
            "👤 Mon profil",
            "💞 Découvrir",
        ]
    )

    # =====================================================
    # MON PROFIL
    # =====================================================

    with profile_tab:

        st.subheader("👤 Mon profil")

        first_name = str(user["first_name"])
        country = str(user["country"])
        city = str(user["city"])
        looking_for = str(user["looking_for"])
        bio = user["bio"] or (
            "Aucune présentation pour le moment."
        )

        initial = (
            first_name[0].upper()
            if first_name
            else "?"
        )

        st.markdown(
            f"""
            <div class="profile-card">

                <div class="avatar">
                    {html.escape(initial)}
                </div>

                <div class="profile-name">
                    {html.escape(first_name)}
                    <span class="profile-age">
                        · {user["age"]} ans
                    </span>
                </div>

                <div class="profile-location">
                    🌍 {html.escape(country)}
                    · 📍 {html.escape(city)}
                </div>

                <div class="profile-looking">
                    ❤️ Recherche :
                    {html.escape(looking_for)}
                </div>

                <div class="profile-bio">
                    <strong>À propos de moi</strong><br><br>
                    {html.escape(str(bio))}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        if user["verified"]:

            st.success("🛡️ Profil vérifié")

        else:

            st.info(
                "⏳ Votre profil pourra être vérifié "
                "prochainement."
            )

        st.caption(
            "📸 Photo, langues, centres d’intérêt et "
            "préférences avancées seront ajoutés dans "
            "les prochaines étapes."
        )

    # =====================================================
    # DÉCOUVRIR
    # =====================================================

    with discover_tab:

        st.subheader("💞 Découvrir")

        st.write(
            "Découvrez des personnes qui recherchent "
            "une relation sincère."
        )

        search_country = st.text_input(
            "🌍 Rechercher par pays",
            placeholder="France, Suisse, Cameroun...",
            key="country_search",
        )

        profiles = get_profiles(
            user["id"],
            search_country.strip(),
        )

        if not profiles:

            st.info(
                "🌍 Aucun autre profil trouvé."
            )

            st.caption(
                "Crée un deuxième profil de test "
                "pour découvrir cette section."
            )

        else:

            columns = st.columns(2)

            for index, profile in enumerate(profiles):

                with columns[index % 2]:

                    first_name = str(
                        profile["first_name"]
                    )

                    country = str(
                        profile["country"]
                    )

                    city = str(
                        profile["city"]
                    )

                    looking_for = str(
                        profile["looking_for"]
                    )

                    bio = profile["bio"] or (
                        "Cette personne n’a pas encore "
                        "ajouté de présentation."
                    )

                    initial = (
                        first_name[0].upper()
                        if first_name
                        else "?"
                    )

                    st.markdown(
                        f"""
                        <div class="profile-card">

                            <div class="avatar">
                                {html.escape(initial)}
                            </div>

                            <div class="profile-name">
                                {html.escape(first_name)}
                                <span class="profile-age">
                                    · {profile["age"]} ans
                                </span>
                            </div>

                            <div class="profile-location">
                                🌍 {html.escape(country)}
                                · 📍 {html.escape(city)}
                            </div>

                            <div class="profile-looking">
                                ❤️ Recherche :
                                {html.escape(looking_for)}
                            </div>

                            <div class="profile-bio">
                                {html.escape(str(bio))}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    if profile["verified"]:

                        st.markdown(
                            '<div class="verified">'
                            "✓ Profil vérifié"
                            "</div>",
                            unsafe_allow_html=True,
                        )

                    like_col, interest_col = st.columns(2)

                    with like_col:

                        if st.button(
                            "❤️ J’aime",
                            key=f"like_{profile['id']}",
                            use_container_width=True,
                        ):

                            st.toast(
                                f"❤️ Intérêt envoyé à "
                                f"{first_name} !"
                            )

                    with interest_col:

                        if st.button(
                            "💌 Intéressé(e)",
                            key=f"interest_{profile['id']}",
                            use_container_width=True,
                        ):

                            st.toast(
                                f"💌 Intérêt envoyé à "
                                f"{first_name}."
                            )


# =========================================================
# VISITEUR
# =========================================================

else:

    # =====================================================
    # HERO
    # =====================================================

    st.markdown(
        """
        <div class="hero">

            <h1>Rencontrez quelqu’un de vrai. ❤️</h1>

            <p>
                LoveConnect rapproche les personnes qui
                recherchent une relation sérieuse, sincère
                et fondée sur le respect.
            </p>

            <p>
                🌍 De l’Europe au monde entier
            </p>

        </div>
        """,
        unsafe_allow_html=True,
    )

    registration_tab, login_tab = st.tabs(
        [
            "❤️ Créer mon profil",
            "🔐 Se connecter",
        ]
    )

    # =====================================================
    # INSCRIPTION
    # =====================================================

    with registration_tab:

        registration = st.session_state.registration
        step = st.session_state.registration_step

        st.markdown(
            f"""
            <div class="step-number">
                ÉTAPE {step} / 3
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.progress(
            step / 3
        )

        # =================================================
        # ÉTAPE 1
        # =================================================

        if step == 1:

            st.markdown(
                """
                <div class="step-card">

                    <div class="step-title">
                        👤 Qui êtes-vous ?
                    </div>

                    <div class="step-description">
                        Commençons par quelques informations
                        simples pour créer votre identité
                        sur LoveConnect.
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("registration_step_1"):

                first_name = st.text_input(
                    "Prénom ou prénom d’affichage",
                    value=registration.get(
                        "first_name",
                        "",
                    ),
                    placeholder="Exemple : Pavel",
                )

                age = st.number_input(
                    "Âge",
                    min_value=18,
                    max_value=100,
                    value=int(
                        registration.get(
                            "age",
                            18,
                        )
                    ),
                )

                gender_options = [
                    "Homme",
                    "Femme",
                    "Autre",
                ]

                current_gender = registration.get(
                    "gender",
                    "Homme",
                )

                gender_index = gender_options.index(
                    current_gender
                )

                gender = st.selectbox(
                    "Je suis",
                    gender_options,
                    index=gender_index,
                )

                next_button = st.form_submit_button(
                    "Continuer →",
                    use_container_width=True,
                )

            if next_button:

                if not first_name.strip():

                    st.error(
                        "Veuillez entrer votre prénom."
                    )

                else:

                    registration["first_name"] = (
                        first_name.strip()
                    )

                    registration["age"] = int(age)

                    registration["gender"] = gender

                    st.session_state.registration = (
                        registration
                    )

                    st.session_state.registration_step = 2

                    st.rerun()

        # =================================================
        # ÉTAPE 2
        # =================================================

        elif step == 2:

            st.markdown(
                """
                <div class="step-card">

                    <div class="step-title">
                        ❤️ Que recherchez-vous ?
                    </div>

                    <div class="step-description">
                        Ces informations aideront les autres
                        membres à mieux comprendre votre
                        recherche et votre personnalité.
                    </div>

                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.form("registration_step_2"):

                looking_options = [
                    "Une femme",
                    "Un homme",
                    "Une personne",
                ]

                current_looking = registration.get(
                    "looking_for",
                    "Une personne",
                )

                looking_for = st.selectbox(
                    "Je recherche",
                    looking_options,
                    index=looking_options.index(
                        current_looking
                    ),
                )

                country = st.text_input(
                    "🌍 Pays",
                    value=registration.get(
                        "country",
                        "",
                    ),
                    placeholder="Exemple : France",
                )

                city = st.text_input(
                    "📍 Ville",
                    value=registration.get(
                        "city",
                        "",
                    ),
                    placeholder="Exemple : Lyon",
                )

                bio = st.text_area(
                    "💬 Votre bio",
                    value=registration.get(
                        "bio",
                        "",
                    ),
                    height=160,
                    max_chars=600,
                    placeholder=(
                        "Présentez-vous : vos passions, "
                        "votre personnalité, ce que vous "
                        "aimez et ce que vous recherchez..."
                    ),
                )

                back_button = st.form_submit_button(
                    "← Retour",
                    use_container_width=True,
                )

                next_button = st.form_submit_button(
                    "Continuer →",
                    use_container_width=True,
                )

