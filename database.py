import sqlite3
import hashlib

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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Verification/migration de la colonne photo
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN photo TEXT")
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

def create_user(first_name, age, gender, looking_for, country, city, email, phone, password, bio, photo_b64=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
        INSERT INTO users (first_name, age, gender, looking_for, country, city, email, phone, password, bio, photo)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (first_name, age, gender, looking_for, country, city, email, phone, hash_password(password), bio, photo_b64))
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
        ORDER BY id DESC
        """, (current_user_id, f"%{country_filter}%"))
    else:
        cursor.execute("SELECT * FROM users WHERE id != ? ORDER BY id DESC", (current_user_id,))
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
