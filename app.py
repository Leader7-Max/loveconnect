import streamlit as st
import re

from database import create_tables, create_user


# =========================================================
# CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="LoveConnect — L'amour n'a pas de frontières",
    page_icon="❤️",
    layout="centered",
    initial_sidebar_state="collapsed"
)


# =========================================================
# BASE DE DONNÉES
# =========================================================

create_tables()


# =========================================================
# STYLE
# =========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #fff7f8 0%,
        #ffffff 50%,
        #fff0f3 100%
    );
}

.main-title {
    text-align: center;
    font-size: 48px;
    font-weight: 800;
    margin-top: 35px;
    color: #b3124a;
}

.subtitle {
    text-align: center;
    font-size: 20px;
    color: #555;
    margin-bottom: 30px;
}

.hero {
    text-align: center;
    padding: 35px 20px;
    border-radius: 25px;
    background: rgba(255,255,255,0.9);
    box-shadow: 0 10px 35px rgba(0,0,0,0.08);
    margin-bottom: 30px;
}

.hero-title {
    font-size: 30px;
    font-weight: 700;
    color: #222;
}

.hero-text {
    font-size: 18px;
    line-height: 1.6;
    color: #555;
}

.warning {
    background: #fff8e8;
    border-left: 5px solid #e0a100;
    padding: 18px;
    border-radius: 12px;
    margin-top: 30px;
    color: #5f4b00;
}

.footer {
    text-align: center;
    color: #777;
    font-size: 13px;
    margin-top: 45px;
    padding-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# TITRE
# =========================================================

st.markdown(
    '<div class="main-title">❤️ LoveConnect</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">L’amour n’a pas de frontières 🌍</div>',
    unsafe_allow_html=True
)


# =========================================================
# PAGE D'ACCUEIL
# =========================================================

st.markdown("""
<div class="hero">

<div class="hero-title">
Trouvez une rencontre sincère ❤️
</div>

<p class="hero-text">
LoveConnect est une plateforme internationale destinée aux personnes
qui recherchent une relation sérieuse, sincère et fondée sur le respect.
</p>

<p class="hero-text">
🇪🇺 De l'Europe au monde entier 🌍
</p>

</div>
""", unsafe_allow_html=True)


# =========================================================
# FORMULAIRE D'INSCRIPTION
# =========================================================

st.markdown("## ❤️ Créer mon profil")

st.info(
    "LoveConnect est réservé aux personnes âgées de 18 ans ou plus."
)

with st.form("registration_form"):

    first_name = st.text_input(
        "Prénom",
        placeholder="Votre prénom"
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
        placeholder="Exemple : France"
    )

    city = st.text_input(
        "Ville",
        placeholder="Exemple : Lyon"
    )

    email = st.text_input(
        "Adresse e-mail",
        placeholder="exemple@email.com"
    )

    phone = st.text_input(
        "Numéro de téléphone",
        placeholder="Optionnel"
    )

    password = st.text_input(
        "Mot de passe",
        type="password",
        placeholder="Choisissez un mot de passe"
    )

    bio = st.text_area(
        "Présentez-vous",
        placeholder="Parlez un peu de vous et de ce que vous recherchez..."
    )

    accept = st.checkbox(
        "J'ai 18 ans ou plus et j'accepte les règles de LoveConnect."
    )

    submitted = st.form_submit_button(
        "❤️ Créer mon profil",
        use_container_width=True
    )


# =========================================================
# TRAITEMENT DU FORMULAIRE
# =========================================================

if submitted:

    if not first_name.strip():
        st.error("Veuillez indiquer votre prénom.")

    elif not country.strip():
        st.error("Veuillez indiquer votre pays.")

    elif not city.strip():
        st.error("Veuillez indiquer votre ville.")

    elif not email.strip():
        st.error("Veuillez indiquer votre adresse e-mail.")

    elif not re.match(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
        email.strip()
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
            email.strip().lower(),
            phone.strip(),
            password,
            bio.strip()
        )

        if success:
            st.success("🎉 " + message)
            st.balloons()

        else:
            st.error("❌ " + message)


# =========================================================
# SÉCURITÉ
# =========================================================

st.markdown("""
<div class="warning">

<strong>🛡️ Sécurité LoveConnect</strong><br><br>

Ne partagez jamais vos informations bancaires, mots de passe
ou documents personnels avec une personne rencontrée en ligne.

Méfiez-vous des demandes d'argent et signalez tout comportement suspect.

Pour une première rencontre, privilégiez toujours un lieu public.

</div>
""", unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">

❤️ LoveConnect — Des rencontres sincères, au-delà des frontières 🌍<br>

Plateforme réservée aux personnes majeures.

</div>
""", unsafe_allow_html=True)
