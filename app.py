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
    page_title="LoveConnect",
    page_icon="❤️",
    layout="wide",
    initial_sidebar_state="collapsed"
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


# =========================================================
# DESIGN
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
        radial-gradient(
            circle at 10% 10%,
            rgba(255, 210, 225, .70),
            transparent 28%
        ),
        radial-gradient(
            circle at 90% 15%,
            rgba(255, 230, 238, .80),
            transparent 28%
        ),
        linear-gradient(
            135deg,
            #fff8fa 0%,
            #ffffff 50%,
            #fff2f6 100%
        );
}

.block-container {
    max-width: 1180px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}


/* LOGO */

.logo {
    text-align: center;
    font-size: 44px;
    font-weight: 900;
    color: #b3134f;
    letter-spacing: -1px;
}

.tagline {
    text-align: center;
    color: #777;
    font-size: 15px;
    margin-bottom: 30px;
}


/* HERO */

.hero {
    background: rgba(255,255,255,.94);
    border-radius: 30px;
    padding: 50px 30px;
    text-align: center;
    box-shadow: 0 20px 60px rgba(100,20,50,.10);
    border: 1px solid rgba(179,19,79,.08);
    margin-bottom: 30px;
}

.hero-title {
    font-size: 45px;
    font-weight: 900;
    color: #222;
}

.hero-text {
    color: #666;
    font-size: 19px;
    line-height: 1.7;
    max-width: 720px;
    margin: auto;
}


/* SECTION */

.section-title {
    font-size: 30px;
    font-weight: 850;
    color: #222;
}

.section-subtitle {
    color: #777;
    margin-bottom: 22px;
}


/* DASHBOARD */

.dashboard {
    background: rgba(255,255,255,.95);
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,.06);
    margin-bottom: 25px;
}


/* PROFILE CARD */

.profile-card {
    background: rgba(255,255,255,.98);
    border-radius: 24px;
    padding: 24px;
    box-shadow: 0 12px 35px rgba(0,0,0,.07);
    border: 1px solid rgba(179,19,79,.08);
    margin-bottom: 12px;
}

.avatar {
    width: 78px;
    height: 78px;
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
    font-size: 31px;
    font-weight: 800;
    margin-bottom: 14px;
}

.name {
    font-size: 25px;
    font-weight: 800;
    color: #222;
}

.age {
    color: #777;
    font-size: 18px;
    font-weight: 500;
}

.location {
    color: #666;
    margin-top: 8px;
    font-size: 15px;
}

.looking {
    color: #b3134f;
    font-weight: 700;
    margin-top: 8px;
}

.bio {
    color: #555;
    line-height: 1.6;
    margin-top: 14px;
}

.badge {
    display: inline-block;
    background: #edf9f0;
    color: #26763d;
    border-radius: 30px;
    padding: 5px 11px;
    font-size: 12px;
    font-weight: 700;
    margin-top: 8px;
}


/* SECURITY */

.security {
    background: #fff8e8;
    border-left: 5px solid #e0a100;
    border-radius: 14px;
    padding: 18px;
    margin-top: 35px;
    color: #5d4b00;
}


/* FOOTER */

.footer {
    text-align: center;
    color: #888;
    font-size: 13px;
    margin-top: 45px;
}


/* MOBILE */

@media (max-width: 700px) {

    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero {
        padding: 35px 20px;
    }

    .hero-title {
        font-size: 31px;
    }

    .logo {
        font-size: 35px;
    }

}

</style>
""", unsafe_allow_html=True)


# =========================================================
# LOGO
# =========================================================

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

    if user is not None:

        # -------------------------------------------------
        # BARRE UTILISATEUR
        # -------------------------------------------------

        top1, top2 = st.columns([4, 1])

        with top1:

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

        with top2:

            if st.button(
                "🚪 Déconnexion",
                use_container_width=True
            ):

                st.session_state.logged_in = False
                st.session_state.user_id = None
                st.session_state.user_name = None
                st.session_state.user_email = None

                st.rerun()


        # -------------------------------------------------
        # NAVIGATION
        # -------------------------------------------------

        profile_tab, discover_tab = st.tabs(
            [
                "👤 Mon profil",
                "💞 Découvrir"
            ]
        )


        # =================================================
        # MON PROFIL
        # =================================================

        with profile_tab:

            st.markdown(
                '<div class="section-title">👤 Mon profil</div>',
                unsafe_allow_html=True
            )

            if user["verified"]:

                st.success("🛡️ Profil vérifié")

            else:

                st.info(
                    "⏳ Votre profil pourra être vérifié prochainement."
                )


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

                    <div class="name">
                        {user["first_name"]}
                        <span class="age">
                            · {user["age"]} ans
                        </span>
                    </div>

                    <div class="location">
                        🌍 {user["country"]}
                        · 📍 {user["city"]}
                    </div>

                    <div class="looking">
                        ❤️ Recherche : {user["looking_for"]}
                    </div>

                    <div class="bio">
                        <strong>À propos de moi</strong><br><br>
                        {bio}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            st.info(
                "🔜 La photo, la modification du profil et la "
                "vérification d'identité seront ajoutées progressivement."
            )


        # =================================================
        # DÉCOUVRIR
        # =================================================

        with discover_tab:

            st.markdown(
                '<div class="section-title">💞 Découvrir</div>',
                unsafe_allow_html=True
            )

            st.markdown(
                '<div class="section-subtitle">'
                'Découvrez des personnes qui recherchent '
                'une relation sincère.'
                '</div>',
                unsafe_allow_html=True
            )


            # -------------------------------------------------
            # RECHERCHE
            # -------------------------------------------------

            search_country = st.text_input(
                "🌍 Rechercher par pays",
                placeholder="France, Suisse, Cameroun...",
                key="search_country"
            )


            profiles = get_profiles(
                user["id"],
                search_country.strip()
            )


            # -------------------------------------------------
            # RÉSULTATS
            # -------------------------------------------------

            if not profiles:

                st.info(
                    "🌍 Aucun autre profil trouvé pour le moment."
                )

                st.caption(
                    "Crée un deuxième faux profil pour tester "
                    "l'espace Découvrir."
                )

            else:

                # Affichage en deux colonnes
                columns = st.columns(2)

                for index, profile in enumerate(profiles):

                    column = columns[index % 2]

                    with column:

                        first_letter = (
                            profile["first_name"][0].upper()
                            if profile["first_name"]
                            else "?"
                        )

                        bio = profile["bio"] or (
                            "Cette personne n'a pas encore ajouté "
                            "de présentation."
                        )

                        st.markdown(
                            '<div class="profile-card">',
                            unsafe_allow_html=True
                        )

                        # Avatar
                        st.markdown(
                            f"""
                            <div class="avatar">
                                {first_letter}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                        # Nom
                        st.markdown(
                            f"""
                            <div class="name">
                                {profile["first_name"]}
                                <span class="age">
                                    · {profile["age"]} ans
                                </span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                        # Vérification
                        if profile["verified"]:

                            st.markdown(
                                '<div class="badge">'
                                '✓ Profil vérifié'
                                '</div>',
                                unsafe_allow_html=True
                            )


                        # Localisation
                        st.markdown(
                            f"""
                            <div class="location">
                                🌍 {profile["country"]}
                                · 📍 {profile["city"]}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                        # Recherche
                        st.markdown(
                            f"""
                            <div class="looking">
                                ❤️ Recherche : {profile["looking_for"]}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                        # Bio
                        st.markdown(
                            f"""
                            <div class="bio">
                                {bio}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                        st.markdown(
                            '</div>',
                            unsafe_allow_html=True
                        )


                        # Boutons
                        like_col, interest_col = st.columns(2)

                        with like_col:

                            if st.button(
                                "❤️ J'aime",
                                key=f"like_{profile['id']}",
                                use_container_width=True
                            ):

                                st.toast(
                                    f"❤️ Intérêt envoyé à {profile['first_name']} !"
                                )


                        with interest_col:

                            if st.button(
                                "💌 Intéressé(e)",
                                key=f"interest_{profile['id']}",
                                use_container_width=True
                            ):

                                st.toast(
                                    f"💌 Votre intérêt pour {profile['first_name']} est enregistré."
                                )


# =========================================================
# NON CONNECTÉ
# =========================================================

else:

    # -----------------------------------------------------
    # HERO
    # -----------------------------------------------------

    st.markdown(
        """
        <div class="hero">

            <div class="hero-title">
                Rencontrez quelqu’un de vrai. ❤️
            </div>

            <br>

            <div class="hero-text">
                LoveConnect rapproche les personnes qui recherchent
                une relation sérieuse, sincère et fondée sur le respect.
            </div>

            <br>

            <div style="font-size:18px;">
                🌍 De l’Europe au monde entier
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    inscription, connexion = st.tabs(
        [
            "❤️ Créer mon profil",
            "🔐 Se connecter"
        ]
    )


    # =====================================================
    # INSCRIPTION
    # =====================================================

    with inscription:

        st.subheader("❤️ Créer votre profil")

        st.info(
            "🔞 LoveConnect est réservé aux personnes âgées de 18 ans ou plus."
        )

        with st.form("registration_form"):

            first_name = st.text_input(
                "Prénom"
            )

            age = st.number_input(
                "Âge",
                min_value=18,
                max_value=100,
                value=18
            )

            gender = st.selectbox(
                "Je suis",
                [
                    "Homme",
                    "Femme",
                    "Autre"
                ]
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
                "Je confirme avoir 18 ans ou plus et accepter les règles de LoveConnect."
            )

            submit = st.form_submit_button(
                "❤️ Créer mon profil",
                use_container_width=True
            )


        if submit:

            email_clean = email.strip().lower()

            if not first_name.strip():

                st.error(
                    "Veuillez entrer votre prénom."
                )

            elif not country.strip():

                st.error(
                    "Veuillez entrer votre pays."
                )

            elif not city.strip():

                st.error(
                    "Veuillez entrer votre ville."
                )

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

    with connexion:

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

                elif verify_pa
