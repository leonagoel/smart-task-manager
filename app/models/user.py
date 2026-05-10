from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from .db import get_conn
from app import login_manager


class User(UserMixin):
    def __init__(self, id, username, email, password_hash, created_at=None):
        self.id = id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at

    # ------------------------------------------------------------------
    # Class-level DB helpers
    # ------------------------------------------------------------------

    @classmethod
    def get_by_id(cls, user_id):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
                row = cur.fetchone()
        finally:
            conn.close()
        if row:
            return cls(**row)
        return None

    @classmethod
    def get_by_email(cls, email):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE email = %s", (email,))
                row = cur.fetchone()
        finally:
            conn.close()
        if row:
            return cls(**row)
        return None

    @classmethod
    def get_by_username(cls, username):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM users WHERE username = %s", (username,))
                row = cur.fetchone()
        finally:
            conn.close()
        if row:
            return cls(**row)
        return None

    @classmethod
    def create(cls, username, email, password):
        password_hash = generate_password_hash(password)
        conn = get_conn()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO users (username, email, password_hash)
                        VALUES (%s, %s, %s)
                        RETURNING *
                        """,
                        (username, email, password_hash),
                    )
                    row = cur.fetchone()
        finally:
            conn.close()
        return cls(**row)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(int(user_id))
