import re
import streamlit as st

from database import (
    create_tables,
    create_user,
    get_user_by_email,
    verify_password
)


st.set_page_config(
    page_title="LoveConnect",
    page_icon="❤️",
    layout="centered"
)


# Création de la base
create_tables()


# Session utilisateur
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "user_name" not in st.session_state:
    st.session_state.user_name = None


# Style
st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #fff7f8,
        #ffffff,
        #fff0f3
    );
}

.title {
    text-align: center;
    color: #b3124a;
    font-size: 46px;
    font-weight: 800;
}

.subtitle {
    text-align: center;
    color: #666;
    font-size: 19px;
    margin-bottom: 30px;
}

.card {
    background: white;
    padding: 25px;
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
}

.footer {
    text-align: center;
    color: #777;
    margin-top: 40px;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)


# Titre
st.markdown(
    '<div class="title">❤️ LoveConnect</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">L’amour n’a pas de frontières 🌍</div>',
    unsafe_allow_html=True
)


# =====================================================
# UTILISATEUR CONNECTÉ
# =====================================================

if st.session_state.logged_in:

    st.success(
        f"❤️ Bienvenue {st.session_state.user_name} !"
    )

    st.markdown(
        """
        <div class="card">
        <h2>Votre espace LoveConnect</h2>
        <p>
        Votre connexion est active.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    if st.button(
        "🚪 Se déconnecter",
        use_container_width=True
    ):
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.rerun()

    st.info(
        "🔜 La recherche de profils sera ajoutée prochainement."
    )


# =====================================================
# NON CONNECTÉ
# =====================================================

else:

    inscription, connexion = st.tabs(
        [
            "❤️ Créer mon profil",
            "🔐 Se connecter"
        ]
    )


    # =================================================
    # INSCRIPTION
    # =================================================

    with inscription:

        st.subheader("❤️ Créer mon profil")

        st.info(
            "LoveConnect est réservé aux personnes âgées de 18 ans ou plus."
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
                "Présentez-vous"
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


    # =================================================
    # CONNEXION
    # =================================================

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

                    st.rerun()

                else:

                    st.error(
                        "❌ E-mail ou mot de passe incorrect."
                    )


# Sécurité
st.warning(
    "🛡️ Ne partagez jamais vos informations bancaires, "
    "mots de passe ou documents personnels avec une personne rencontrée en ligne."
)


# Pied de page
st.markdown(
    """
    <div class="footer">
    ❤️ LoveConnect — Des rencontres sincères, au-delà des frontières 🌍<br>
    Plateforme réservée aux personnes majeures.
    </div>
    """,
    unsafe_allow_html=True
                )
