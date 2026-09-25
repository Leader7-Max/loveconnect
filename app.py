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
    color: #5c4900;
}


/* FOOTER */

.love-footer {
    text-align: center;
    color: #888;
    padding: 40px 0 15px;
    font-size: 13px;
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

    .hero h1 {
        font-size: 32px;
    }

    .logo {
        font-size: 34px;
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
    '<div class="tagline">L’amour n’a pas de frontières · Europe → Monde 🌍</div>',
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

        # =================================================
        # BARRE UTILISATEUR
        # =================================================

        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(
                f"""
                <div class="dashboard">
                ❤️ <strong>Bonjour {user["first_name"]}</strong><br>
                <span style="color:#777;">
                Bienvenue dans votre espace LoveConnect.
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


        # =================================================
        # NAVIGATION
        # =================================================

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
                '<div class="section-title">Mon profil</div>',
                unsafe_allow_html=True
            )

            verified = (
                '<span class="verified">✓ Profil vérifié</span>'
                if user["verified"]
                else '<span class="verified">⏳ Vérification en attente</span>'
            )

            bio = user["bio"] or (
                "Ajoutez une présentation pour permettre aux autres "
                "membres de mieux vous découvrir."
            )

            st.markdown(
                f"""
                <div class="profile-card">

                    <div class="profile-avatar">
                        {user["first_name"][0].upper()}
                    </div>

                    <div class="profile-name">
                        {user["first_name"]}
                        <span class="profile-age">
                            · {user["age"]} ans
                        </span>
                    </div>

                    <div style="margin-top:8px;">
                        {verified}
                    </div>

                    <div class="profile-location">
                        🌍 {user["country"]} · 📍 {user["city"]}
                    </div>

                    <div class="profile-looking">
                        ❤️ Recherche : {user["looking_for"]}
                    </div>

                    <div class="profile-bio">
                        <strong>À propos de moi</strong><br>
                        {bio}
                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )

            st.info(
                "🔜 La modification du profil et l'ajout de photo "
                "seront disponibles prochainement."
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
                'Découvrez des personnes qui recherchent une relation sincère.'
                '</div>',
                unsafe_allow_html=True
            )


            # Recherche
            search_country = st.text_input(
                "🌍 Rechercher par pays",
                placeholder="Exemple : France, Suisse, Cameroun...",
                key="search_country"
            )


            profiles = get_profiles(
                user["id"],
                search_country.strip()
            )


            if not profiles:

                st.info(
                    "🌍 Aucun autre profil ne correspond encore à votre recherche."
                )

            else:

                for profile in profiles:

                    first_letter = (
                        profile["first_name"][0].upper()
                        if profile["first_name"]
                        else "?"
                    )

                    verified = (
                        '<span class="verified">✓ Vérifié</span>'
                        if profile["verified"]
                        else ""
                    )

                    bio = profile["bio"] or (
                        "Cette personne n'a pas encore ajouté de présentation."
                    )

                    st.markdown(
                        f"""
                        <div class="profile-card">

                            <div class="profile-avatar">
                                {first_letter}
                            </div>

                            <div class="profile-name">
                                {profile["first_name"]}
                                <span class="profile-age">
                                    · {profile["age"]} ans
                                </span>
                            </div>

                            <div style="margin-top:7px;">
                                {verified}
                            </div>

                            <div class="profile-location">
                                🌍 {profile["country"]}
                                · 📍 {profile["city"]}
                            </div>

                            <div class="profile-looking">
                                ❤️ Recherche : {profile["looking_for"]}
                            </div>

                            <div class="profile-bio">
                                {bio}
                            </div>

                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    like_col, message_col = st.columns(2)

                    with like_col:
                        st.button(
                            "❤️ J’aime",
                            key=f"like_{profile['id']}",
                            use_container_width=True
                        )

                    with message_col:
                        st.button(
                            "💌 Intéressé(e)",
                            key=f"interest_{profile['id']}",
                            use_container_width=True
                        )


# =========================================================
# NON CONNECTÉ
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

            <p style="margin-top:18px;">
            🌍 De l’Europe au monde entier
            </p>

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

        st.subheader("Créer votre profil")

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
                placeholder="Parlez de vous, de vos passions et de ce que vous recherchez..."
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

                st.error("Veuillez entrer votre prénom.")

            elif not country.strip():

                st.error("Veuillez entrer votre pays.")

            elif not city.strip():

                st.error("Veuillez entrer votre ville.")

            elif not re.match(
                r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
                email_clean
            ):

                st.error("Veuillez entrer une adresse e-mail valide.")

            elif len(password) < 6:

                st.error(
                    "Le mot de passe doit contenir au moins 6 caractères."
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
                    "Veuillez entrer votre e-mail et votre mot de passe."
                )

            else:

                user = get_user_by_email(
                    email_clean
                )

                if user is None:

                    st.error(
                        "❌ E-mail ou mot de passe incorrect."
                    )

                elif verify_password(
                    login_password,
                    user["password"]
                ):

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
# SÉCURITÉ
# =========================================================

st.markdown(
    """
    <div class="security">

    <strong>🛡️ Votre sécurité avant tout</strong><br><br>

    Ne partagez jamais vos coordonnées bancaires, mots de passe
    ou documents personnels avec une personne rencontrée en ligne.

    Méfiez-vous des demandes d'argent et signalez tout comportement suspect.

    Pour une première rencontre, privilégiez toujours un lieu public.

    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="love-footer">

    ❤️ <strong>LoveConnect</strong><br>
    Des rencontres sincères, au-delà des frontières 🌍<br><br>
    🔞 Plateforme réservée aux personnes majeures.

    </div>
    """,
    unsafe_allow_html=True
  )
