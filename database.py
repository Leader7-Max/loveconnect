import sqlite3
import hashlib
from datetime import datetime, timedelta

DB_NAME = "loveconnect.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, hashed):
    return hash_password(password) == hashed

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
    
    # Migrations douces pour ajouter les colonnes manquantes sur les anciennes bases
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN photo TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_seen TIMESTAMP")
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
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER NOT NULL,
        receiver_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        is_read INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    conn.commit()
    conn.close()

def update_last_seen(user_id):
    """Met à jour l'horodatage de la dernière activité de l'utilisateur"""
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE users SET last_seen = ? WHERE id = ?", (now_str, user_id))
    conn.commit()
    conn.close()

def format_last_seen(last_seen_str):
    """Calcule et affiche le statut En ligne ou Vu il y a X min/heures/jours"""
    if not last_seen_str:
        return '<span style="color: #6c757d; font-size: 11px;">⏱️ Hors ligne</span>'
    
    try:
        last_seen_dt = datetime.strptime(str(last_seen_str).split('.')[0], "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - last_seen_dt
        minutes = int(diff.total_seconds() / 60)

        if minutes < 5:
            return '<span style="color: #2b9348; font-weight: 600; font-size: 11px;">🟢 En ligne</span>'
        elif minutes < 60:
            return f'<span style="color: #6c757d; font-size: 11px;">⏱️ Vu il y a {minutes} min</span>'
        elif minutes < 1440:
            hours = minutes // 60
            return f'<span style="color: #6c757d; font-size: 11px;">⏱️ Vu il y a {hours}h</span>'
        else:
            days = minutes // 1440
            return f'<span style="color: #6c757d; font-size: 11px;">⏱️ Vu il y a {days}j</span>'
    except Exception:
        return '<span style="color: #6c757d; font-size: 11px;">⏱️ Hors ligne</span>'

def create_user(first_name, age, gender, looking_for, country, city, email, phone, password, bio, photo_b64=None):
    conn = get_connection()
    cursor = conn.cursor()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cursor.execute("""
        INSERT INTO users (first_name, age, gender, looking_for, country, city, email, phone, password, bio, photo, last_seen)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, age, gender, looking_for, country, city, email, phone, hash_password(password), bio, photo_b64, now_str))
        conn.commit()
        return True, "Compte créé avec succès."
    except sqlite3.IntegrityError:
        return False, "Cet e-mail est déjà utilisé."
    finally:
        conn.close()

def update_user_photo(user_id, photo_b64):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET photo = ? WHERE id = ?", (photo_b64, user_id))
    conn.commit()
    conn.close()

def get_user_by_email(email):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    return user

def get_profiles(current_user_id, country_filter=""):
    conn = get_connection()
    cursor = conn.cursor()
    if country_filter:
        cursor.execute("""
        SELECT * FROM users 
        WHERE id != ? AND LOWER(country) LIKE LOWER(?)
        ORDER BY last_seen DESC, id DESC
        """, (current_user_id, f"%{country_filter}%"))
    else:
        cursor.execute("SELECT * FROM users WHERE id != ? ORDER BY last_seen DESC, id DESC", (current_user_id,))
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
        conn.close()
        return True, is_match
    except sqlite3.IntegrityError:
        conn.close()
        return False, False

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

def send_message(sender_id, receiver_id, content):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)", (sender_id, receiver_id, content))
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
