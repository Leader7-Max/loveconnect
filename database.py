"""
LoveConnect — Couche d'accès aux données (SQLite)
Gère : comptes, profils, likes/pass, matches, blocage, signalements,
messagerie (avec statut lu/non lu) et statistiques.
"""

import sqlite3
import hashlib
from datetime import datetime

DB_NAME = "loveconnect.db"

GENDER_FOR_PREFERENCE = {
    "Un homme": "Homme",
    "Une femme": "Femme",
    # "Une personne" -> aucun filtre de genre appliqué
}


# ---------------------------------------------------------------------------
# Connexion & sécurité
# ---------------------------------------------------------------------------

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password, hashed):
    return hash_password(password) == hashed


# ---------------------------------------------------------------------------
# Schéma
# ---------------------------------------------------------------------------

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        age INTEGER NOT NULL,
        gender TEXT NOT NULL,
        looking_for TEXT NOT NULL,
        country TEXT NOT NULL,
        city TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        phone TEXT,
        password TEXT NOT NULL,
        bio TEXT,
        photo TEXT,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Migrations douces pour les bases déjà existantes
    for column, col_type in [("photo", "TEXT"), ("last_seen", "TIMESTAMP")]:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column} {col_type}")
        except sqlite3.OperationalError:
            pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS likes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(sender_id, receiver_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS passes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(sender_id, receiver_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS blocked_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        blocked_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, blocked_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reporter_id INTEGER NOT NULL,
        reported_id INTEGER NOT NULL,
        reason TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_pair ON messages(sender_id, receiver_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_likes_pair ON likes(sender_id, receiver_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_passes_pair ON passes(sender_id, receiver_id)")

    conn.commit()
    conn.close()


# ---------------------------------------------------------------------------
# Présence
# ---------------------------------------------------------------------------

def update_last_seen(user_id):
    """Met à jour l'horodatage de la dernière activité de l'utilisateur."""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE users SET last_seen = ? WHERE id = ?", (now_str, user_id))
    conn.commit()
    conn.close()


def format_last_seen(last_seen_str):
    """Calcule et affiche le statut En ligne ou Vu il y a X min/heures/jours."""
    if not last_seen_str:
        return '<span style="color:#94a3b8;font-size:11px;">⏱️ Hors ligne</span>'

    try:
        last_seen_dt = datetime.strptime(str(last_seen_str).split('.')[0], "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - last_seen_dt
        minutes = int(diff.total_seconds() / 60)

        if minutes < 5:
            return '<span style="color:#16a34a;font-weight:700;font-size:11px;">🟢 En ligne</span>'
        elif minutes < 60:
            return f'<span style="color:#94a3b8;font-size:11px;">⏱️ Vu il y a {minutes} min</span>'
        elif minutes < 1440:
            hours = minutes // 60
            return f'<span style="color:#94a3b8;font-size:11px;">⏱️ Vu il y a {hours}h</span>'
        else:
            days = minutes // 1440
            return f'<span style="color:#94a3b8;font-size:11px;">⏱️ Vu il y a {days}j</span>'
    except Exception:
        return '<span style="color:#94a3b8;font-size:11px;">⏱️ Hors ligne</span>'


def is_online(last_seen_str, threshold_minutes=5):
    if not last_seen_str:
        return False
    try:
        last_seen_dt = datetime.strptime(str(last_seen_str).split('.')[0], "%Y-%m-%d %H:%M:%S")
        minutes = (datetime.now() - last_seen_dt).total_seconds() / 60
        return minutes < threshold_minutes
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Comptes
# ---------------------------------------------------------------------------

def create_user(first_name, age, gender, looking_for, country, city, email, phone, password, bio, photo_b64=None):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("""
        INSERT INTO users (first_name, age, gender, looking_for, country, city, email, phone, password, bio, photo, last_seen)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, age, gender, looking_for, country, city, email, phone,
              hash_password(password), bio, photo_b64, now_str))
        conn.commit()
        return True, "Compte créé avec succès."
    except sqlite3.IntegrityError:
        return False, "Cet e-mail est déjà utilisé."
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def update_user_photo(user_id, photo_b64):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET photo = ? WHERE id = ?", (photo_b64, user_id))
    conn.commit()
    conn.close()


def update_profile(user_id, bio, country, city, looking_for):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET bio = ?, country = ?, city = ?, looking_for = ? WHERE id = ?
    """, (bio, country, city, looking_for, user_id))
    conn.commit()
    conn.close()
    return True


def change_password(user_id, old_password, new_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if not row or not verify_password(old_password, row["password"]):
        conn.close()
        return False, "Mot de passe actuel incorrect."
    cursor.execute("UPDATE users SET password = ? WHERE id = ?", (hash_password(new_password), user_id))
    conn.commit()
    conn.close()
    return True, "Mot de passe mis à jour avec succès."


def delete_account(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    cursor.execute("DELETE FROM likes WHERE sender_id = ? OR receiver_id = ?", (user_id, user_id))
    cursor.execute("DELETE FROM passes WHERE sender_id = ? OR receiver_id = ?", (user_id, user_id))
    cursor.execute("DELETE FROM blocked_users WHERE user_id = ? OR blocked_id = ?", (user_id, user_id))
    cursor.execute("DELETE FROM messages WHERE sender_id = ? OR receiver_id = ?", (user_id, user_id))
    conn.commit()
    conn.close()
    return True


# ---------------------------------------------------------------------------
# Découverte / profils
# ---------------------------------------------------------------------------

def get_profiles(current_user_id, country_filter="", city_filter="", min_age=None, max_age=None,
                  respect_preferences=True):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT gender, looking_for FROM users WHERE id = ?", (current_user_id,))
    me = cursor.fetchone()

    query = """
        SELECT u.* FROM users u
        WHERE u.id != ?
        AND u.id NOT IN (SELECT receiver_id FROM likes WHERE sender_id = ?)
        AND u.id NOT IN (SELECT receiver_id FROM passes WHERE sender_id = ?)
        AND u.id NOT IN (SELECT blocked_id FROM blocked_users WHERE user_id = ?)
        AND u.id NOT IN (SELECT user_id FROM blocked_users WHERE blocked_id = ?)
    """
    params = [current_user_id, current_user_id, current_user_id, current_user_id, current_user_id]

    if respect_preferences and me and me["looking_for"] in GENDER_FOR_PREFERENCE:
        query += " AND u.gender = ?"
        params.append(GENDER_FOR_PREFERENCE[me["looking_for"]])

    if country_filter:
        query += " AND LOWER(u.country) LIKE LOWER(?)"
        params.append(f"%{country_filter}%")

    if city_filter:
        query += " AND LOWER(u.city) LIKE LOWER(?)"
        params.append(f"%{city_filter}%")

    if min_age is not None:
        query += " AND u.age >= ?"
        params.append(min_age)

    if max_age is not None:
        query += " AND u.age <= ?"
        params.append(max_age)

    query += " ORDER BY u.last_seen DESC, u.id DESC"

    cursor.execute(query, params)
    profiles = cursor.fetchall()
    conn.close()
    return profiles


def send_like(sender_id, receiver_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO likes (sender_id, receiver_id) VALUES (?, ?)", (sender_id, receiver_id))
        conn.commit()

        cursor.execute("SELECT id FROM likes WHERE sender_id = ? AND receiver_id = ?", (receiver_id, sender_id))
        is_match = cursor.fetchone() is not None
        return True, is_match
    except sqlite3.IntegrityError:
        return False, False
    finally:
        conn.close()


def pass_profile(sender_id, receiver_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO passes (sender_id, receiver_id) VALUES (?, ?)", (sender_id, receiver_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_users_who_liked_me(user_id):
    """Profils qui m'ont aimé mais que je n'ai pas encore aimés en retour (pas encore un match)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.*, l.created_at as liked_at FROM users u
        INNER JOIN likes l ON u.id = l.sender_id
        WHERE l.receiver_id = ?
        AND u.id NOT IN (SELECT receiver_id FROM likes WHERE sender_id = ?)
        AND u.id NOT IN (SELECT blocked_id FROM blocked_users WHERE user_id = ?)
        AND u.id NOT IN (SELECT user_id FROM blocked_users WHERE blocked_id = ?)
        ORDER BY l.created_at DESC
    """, (user_id, user_id, user_id, user_id))
    res = cursor.fetchall()
    conn.close()
    return res


def get_matches(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT u.* FROM users u
    INNER JOIN likes l1 ON u.id = l1.receiver_id
    INNER JOIN likes l2 ON u.id = l2.sender_id
    WHERE l1.sender_id = ? AND l2.receiver_id = ?
    ORDER BY u.last_seen DESC
    """, (user_id, user_id))
    matches = cursor.fetchall()
    conn.close()
    return matches


def unmatch(user1_id, user2_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM likes WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
    """, (user1_id, user2_id, user2_id, user1_id))
    conn.commit()
    conn.close()
    return True


# ---------------------------------------------------------------------------
# Blocage & signalement
# ---------------------------------------------------------------------------

def block_user(user_id, blocked_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO blocked_users (user_id, blocked_id) VALUES (?, ?)", (user_id, blocked_id))
        cursor.execute("""
            DELETE FROM likes WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        """, (user_id, blocked_id, blocked_id, user_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def unblock_user(user_id, blocked_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blocked_users WHERE user_id = ? AND blocked_id = ?", (user_id, blocked_id))
    conn.commit()
    conn.close()
    return True


def get_blocked_users(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT u.* FROM users u
        INNER JOIN blocked_users b ON u.id = b.blocked_id
        WHERE b.user_id = ?
        ORDER BY b.created_at DESC
    """, (user_id,))
    res = cursor.fetchall()
    conn.close()
    return res


def report_user(reporter_id, reported_id, reason):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO reports (reporter_id, reported_id, reason) VALUES (?, ?, ?)",
                   (reporter_id, reported_id, reason))
    conn.commit()
    conn.close()
    return True


# ---------------------------------------------------------------------------
# Messagerie
# ---------------------------------------------------------------------------

def send_message(sender_id, receiver_id, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)",
                   (sender_id, receiver_id, content))
    conn.commit()
    conn.close()
    return True


def get_messages(user1_id, user2_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT * FROM messages
    WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
    ORDER BY created_at ASC
    """, (user1_id, user2_id, user2_id, user1_id))
    messages = cursor.fetchall()
    conn.close()
    return messages


def mark_messages_read(receiver_id, sender_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE messages SET is_read = 1 WHERE receiver_id = ? AND sender_id = ? AND is_read = 0
    """, (receiver_id, sender_id))
    conn.commit()
    conn.close()


def get_unread_count(receiver_id, sender_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT COUNT(*) as c FROM messages WHERE receiver_id = ? AND sender_id = ? AND is_read = 0
    """, (receiver_id, sender_id))
    row = cursor.fetchone()
    conn.close()
    return row["c"] if row else 0


def get_total_unread(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as c FROM messages WHERE receiver_id = ? AND is_read = 0", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row["c"] if row else 0


def delete_conversation(user1_id, user2_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        DELETE FROM messages WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
    """, (user1_id, user2_id, user2_id, user1_id))
    conn.commit()
    conn.close()
    return True


# ---------------------------------------------------------------------------
# Statistiques
# ---------------------------------------------------------------------------

def get_stats(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as c FROM likes WHERE sender_id = ?", (user_id,))
    likes_sent = cursor.fetchone()["c"]

    cursor.execute("SELECT COUNT(*) as c FROM likes WHERE receiver_id = ?", (user_id,))
    likes_received = cursor.fetchone()["c"]

    cursor.execute("""
        SELECT COUNT(*) as c FROM likes l1
        INNER JOIN likes l2 ON l1.sender_id = l2.receiver_id AND l1.receiver_id = l2.sender_id
        WHERE l1.sender_id = ?
    """, (user_id,))
    matches_count = cursor.fetchone()["c"]

    conn.close()
    return {
        "likes_sent": likes_sent,
        "likes_received": likes_received,
        "matches": matches_count,
  }
      
