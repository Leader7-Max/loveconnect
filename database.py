import hashlib
import secrets
import sqlite3

DATABASE_NAME = "loveconnect.db"


def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_connection()

    conn.execute("""
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
            verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id),
            UNIQUE(sender_id, receiver_id)
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    salt = secrets.token_bytes(16)
    hashed = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 200000
    )
    return salt.hex() + ":" + hashed.hex()


def verify_password(password, stored_password):
    try:
        salt_hex, hash_hex = stored_password.split(":", 1)
        salt = bytes.fromhex(salt_hex)
        hashed = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, 200000
        )
        return secrets.compare_digest(hashed.hex(), hash_hex)
    except Exception:
        return False


def create_user(
    first_name, age, gender, looking_for, country, city, email, phone, password, bio
):
    conn = get_connection()
    try:
        secure_password = hash_password(password)
        conn.execute("""
            INSERT INTO users (
                first_name, age, gender, looking_for,
                country, city, email, phone, password, bio
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            first_name, age, gender, looking_for,
            country, city, email, phone, secure_password, bio
        ))
        conn.commit()
        return True, "Profil créé avec succès."
    except sqlite3.IntegrityError:
        return False, "Cette adresse e-mail est déjà utilisée."
    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_connection()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    return user


def get_profiles(current_user_id, country=""):
    conn = get_connection()
    query = "SELECT * FROM users WHERE id != ?"
    params = [current_user_id]

    if country:
        query += " AND country LIKE ?"
        params.append("%" + country + "%")

    query += " ORDER BY created_at DESC"
    profiles = conn.execute(query, params).fetchall()
    conn.close()
    return profiles


def send_like(sender_id, receiver_id):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO likes (sender_id, receiver_id) VALUES (?, ?)",
            (sender_id, receiver_id),
        )
        conn.commit()

        mutual = conn.execute("""
            SELECT id FROM likes 
            WHERE sender_id = ? AND receiver_id = ?
        """, (receiver_id, sender_id)).fetchone()

        conn.close()
        return True, (mutual is not None)
    except sqlite3.IntegrityError:
        conn.close()
        return False, False


def get_matches(user_id):
    conn = get_connection()
    query = """
        SELECT u.* FROM users u
        INNER JOIN likes l1 ON u.id = l1.receiver_id
        INNER JOIN likes l2 ON u.id = l2.sender_id
        WHERE l1.sender_id = ? AND l2.receiver_id = ?
    """
    matches = conn.execute(query, (user_id, user_id)).fetchall()
    conn.close()
    return matches


def send_message(sender_id, receiver_id, content):
    if not content.strip():
        return False
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (sender_id, receiver_id, content) VALUES (?, ?, ?)",
        (sender_id, receiver_id, content.strip()),
    )
    conn.commit()
    conn.close()
    return True


def get_messages(user_id_1, user_id_2):
    conn = get_connection()
    messages = conn.execute("""
        SELECT * FROM messages 
        WHERE (sender_id = ? AND receiver_id = ?) 
           OR (sender_id = ? AND receiver_id = ?)
        ORDER BY created_at ASC
    """, (user_id_1, user_id_2, user_id_2, user_id_1)).fetchall()
    conn.close()
    return messages
      
