import sqlite3
import os
import streamlit as st
from PIL import Image

# Configuration de la page
st.set_page_config(
    page_title="LoveConnect", page_icon="❤️", layout="centered"
)

DB_PATH = "loveconnect.db"
UPLOAD_DIR = "uploads"


# --- INITIALISATION DE LA BASE DE DONNÉES ---
def init_db():
  os.makedirs(UPLOAD_DIR, exist_ok=True)
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()

  # Table des utilisateurs
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            age INTEGER,
            bio TEXT,
            photo TEXT
        )
    """)

  # Table des likes
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            user_id INTEGER,
            liked_user_id INTEGER,
            PRIMARY KEY (user_id, liked_user_id)
        )
    """)

  # Table des messages
  cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            message TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()


# --- FONCTIONS UTILITAIRES ---
def get_all_users():
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute("SELECT id, username, age, bio, photo FROM users")
  users = cursor.fetchall()
  conn.close()
  return users


def get_user_by_id(user_id):
  conn = sqlite3.connect(DB_PATH)
  cursor = conn.cursor()
  cursor.execute(
      "SELECT id, username, age, bio, photo FROM users WHERE id = ?", (user_id,)
  )
  user = cursor.fetchone()
  conn.close()
  return user


def save_photo(uploaded_file):
  if uploaded_file is not None:
    path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    with open(path, "wb") as f:
      f.write(uploaded_file.getbuffer())
    return path
  return None


# --- GESTION DE LA SESSION ---
if "user_id" not in st.session_state:
  st.session_state["user_id"] = None

# --- BARRE LATÉRALE (NAVIGATION & CONNEXION) ---
st.sidebar.title("❤️ LoveConnect")

users = get_all_users()

if st.session_state["user_id"] is None:
  st.sidebar.subheader("Connexion / Inscription")

  # Création d'un profil
  with st.sidebar.expander("Créer un profil"):
    new_username = st.text_input("Prénom / Pseudo")
    new_age = st.number_input("Âge", min_value=18, max_value=100, value=25)
    new_bio = st.text_area("Bio")
    new_photo = st.file_uploader(
        "Photo de profil", type=["jpg", "png", "jpeg"]
    )

    if st.button("S'inscrire"):
      if new_username:
        photo_path = save_photo(new_photo)
        try:
          conn = sqlite3.connect(DB_PATH)
          cursor = conn.cursor()
          cursor.execute(
              "INSERT INTO users (username, age, bio, photo) VALUES (?, ?, ?,"
              " ?)",
              (new_username, new_age, new_bio, photo_path),
          )
          conn.commit()
          conn.close()
          st.sidebar.success("Compte créé avec succès ! Connecte-toi ci-dessous.")
          st.rerun()
        except sqlite3.IntegrityError:
          st.sidebar.error("Ce pseudo est déjà pris.")
      else:
        st.sidebar.error("Entre un pseudo valide.")

  # Sélection du profil existant
  if users:
    user_options = {u[1]: u[0] for u in users}
    selected_username = st.sidebar.selectbox(
        "Choisir ton profil", list(user_options.keys())
    )
    if st.sidebar.button("Se connecter"):
      st.session_state["user_id"] = user_options[selected_username]
      st.rerun()
  else:
    st.sidebar.info("Aucun profil pour l'instant. Crée le tien !")

else:
  current_user = get_user_by_id(st.session_state["user_id"])
  st.sidebar.success(f"Connecté en tant que : **{current_user[1]}**")
  if st.sidebar.button("Se déconnecter"):
    st.session_state["user_id"] = None
    st.rerun()


# --- INTERFACE PRINCIPALE ---
if st.session_state["user_id"] is None:
  st.title("Bienvenue sur LoveConnect 💖")
  st.write(
      "Connecte-toi ou crée un profil via le menu de gauche pour commencer à"
      " matcher !"
  )

  if users:
    st.subheader("Membres inscrits :")
    for u in users:
      cols = st.columns([1, 3])
      with cols[0]:
        if u[4] and os.path.exists(u[4]):
          st.image(u[4], width=80)
        else:
          st.write("👤 Pas de photo")
      with cols[1]:
        st.write(f"**{u[1]}**, {u[2] ans} - {u[3]}")
  else:
  # Reste du code de l'application principale...
