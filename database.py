import sqlite3
import hashlib
import secrets

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

    conn.commit()
    conn.close()


def hash_password(password):
    salt = secrets.token_bytes(16)

    hashed = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200000
    )

    return salt.hex() + ":" + hashed.hex()


def verify_password(password, stored_password):
    try:
        salt_hex, hash_hex = stored_password.split(":", 1)

        salt = bytes.fromhex(salt_hex)

        hashed = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200000
        )

        return secrets.compare_digest(
            hashed.hex(),
            hash_hex
        )

    except Exception:
        return False


def create_user(
    first_name,
    age,
    gender,
    looking_for,
    country,
    city,
    email,
    phone,
    password,
    bio
):
    conn = get_connection()

    try:
        secure_password = hash_password(password)

        conn.execute("""
            INSERT INTO users (
                first_name,
                age,
                gender,
                looking_for,
                country,
                city,
                email,
                phone,
                password,
                bio
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            first_name,
            age,
            gender,
            looking_for,
            country,
            city,
            email,
            phone,
            secure_password,
            bio
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
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()

    conn.close()

    return user
