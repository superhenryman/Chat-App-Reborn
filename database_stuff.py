import logging
import os
import time
import psycopg2
from argon2 import PasswordHasher
ph = PasswordHasher()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    retry_count = 5
    for i in range(retry_count):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return conn
        except Exception as e:
            logging.error(f"Attempt {i+1} failed: {e}")
            time.sleep(2**i)
    raise Exception("I can't connect :(")


def init_db():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS users(
                        id SERIAL PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL
                    );
                """)
                conn.commit()
    except Exception as e:
        logging.error(f"Error occurred initializing the database: {e}")


def init_banned_db():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS banned(
                        id SERIAL PRIMARY KEY,
                        username TEXT NOT NULL UNIQUE
                    );
                """)
                conn.commit()
    except Exception as e:
        logging.error(f"Error occurred initializing the banned database: {e}")


def create_user(username: str, password: str):
    try:
        hashed = ph.hash(password)
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                    (username, hashed),
                )
                conn.commit()
    except Exception as e:
        logging.error(f"Error while creating user: {e}")


def user_is_banned(username: str) -> bool:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT EXISTS (SELECT 1 FROM banned WHERE username = %s)",
                    (username,),
                )
                return cur.fetchone()[0]
    except Exception as e:
        logging.error(f"Error in is_user_banned(): {e}")
        return False


def reset_password(username: str, password: str, id: int) -> bool:
    try:
        hashed = ph.hash(password)
        if user_is_banned(username):
            logging.info("User banned. Will not continue.")
            return False
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE users SET password = %s WHERE username = %s AND id = %s",
                    (hashed, username, id),
                )
                conn.commit()
                return cur.rowcount > 0 
    except Exception as e:
        logging.error(f"Error in reset_password(): {e}")
        return False


def user_exists(username: str, password: str) -> bool:
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT password FROM users WHERE username = %s",
                    (username,),
                )
                row = cur.fetchone()
                if not row:
                    return False
                stored_hash = row[0]
                return ph.verify(stored_hash, password)
    except Exception as e:
        logging.error(f"Error in is_user_exists(): {e}")
        return False
