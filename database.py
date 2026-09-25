import sqlite3

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
            password,
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
