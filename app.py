import streamlit as st

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

st.set_page_config(
    page_title="LoveConnect — L'amour n'a pas de frontières",
    page_icon="❤️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# STYLE
# ---------------------------------------------------------

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #fff7f8 0%, #ffffff 50%, #fff0f3 100%);
    }

    .main-title {
        text-align: center;
        font-size: 48px;
        font-weight: 800;
        margin-top: 40px;
        margin-bottom: 5px;
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
        background: rgba(255,255,255,0.85);
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

    .feature {
        background: white;
        padding: 20px;
        border-radius: 18px;
        margin: 10px 0;
        box-shadow: 0 5px 20px rgba(0,0,0,0.06);
    }

    .feature-title {
        font-size: 19px;
        font-weight: 700;
        color: #b3124a;
    }

    .feature-text {
        color: #666;
        font-size: 15px;
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

# ---------------------------------------------------------
# LOGO / TITRE
# ---------------------------------------------------------

st.markdown(
    '<div class="main-title">❤️ LoveConnect</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">L’amour n’a pas de frontières 🌍</div>',
    unsafe_allow_html=True
)

# ---------------------------------------------------------
# PRESENTATION
# ---------------------------------------------------------

st.markdown("""
<div class="hero">

<div class="hero-title">
Trouvez une rencontre sincère
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

# ---------------------------------------------------------
# BOUTONS
# ---------------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    if st.button("❤️ Créer mon profil", use_container_width=True):
        st.info("La création de profil sera disponible dans la prochaine étape.")

with col2:
    if st.button("🔐 Se connecter", use_container_width=True):
        st.info("La connexion sera disponible dans la prochaine étape.")

# ---------------------------------------------------------
# VALEURS
# ---------------------------------------------------------

st.markdown("## 💕 Notre vision")

st.markdown("""
<div class="feature">
<div class="feature-title">🌍 Des rencontres internationales</div>
<div class="feature-text">
Découvrez des personnes de différents pays et différentes cultures.
</div>
</div>

<div class="feature">
<div class="feature-title">❤️ Des relations sérieuses</div>
<div class="feature-text">
Une plateforme pensée pour celles et ceux qui recherchent une véritable
connexion et une relation sincère.
</div>
</div>

<div class="feature">
<div class="feature-title">🛡️ Une communauté protégée</div>
<div class="feature-text">
Respect, sécurité et lutte contre les comportements abusifs sont au cœur
de LoveConnect.
</div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# AVERTISSEMENT
# ---------------------------------------------------------

st.markdown("""
<div class="warning">
<strong>🛡️ Protégez-vous</strong><br><br>

Ne partagez jamais vos informations bancaires, mots de passe ou documents
personnels avec une personne rencontrée en ligne.

Méfiez-vous des demandes d'argent et signalez tout comportement suspect.

Pour une première rencontre, privilégiez toujours un lieu public.
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------

st.markdown("""
<div class="footer">
❤️ LoveConnect — Des rencontres sincères, au-delà des frontières 🌍<br>
Plateforme réservée aux personnes majeures.
</div>
""", unsafe_allow_html=True)
