import sqlite3
import hashlib
import secrets


DATABASE_NAME = "loveconnect.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def create_tables():
    connection = get_connection()
    cursor = connection.cursor()

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
            verified INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def hash_password(password):
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200000
    )

    return salt.hex() + ":" + password_hash.hex()


def verify_password(password, stored_password):
    try:
        salt_hex, hash_hex = stored_password.split(":")

        salt = bytes.fromhex(salt_hex)

        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200000
        )

        return secrets.compare_digest(
            password_hash.hex(),
            hash_hex
        )

    except (ValueError, TypeError):
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
    connection = get_connection()
    cursor = connection.cursor()

    try:
        secure_password = hash_password(password)

        cursor.execute("""
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

        connection.commit()

        return True, "Profil créé avec succès."

    except sqlite3.IntegrityError:
        return False, "Cette adresse e-mail est déjà utilisée."

    finally:
        connection.close()


def get_user_by_email(email):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()

    connection.close()

    return user
