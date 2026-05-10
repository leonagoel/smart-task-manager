import psycopg2
import psycopg2.extras
from flask import current_app


def get_conn():
    """Return a new psycopg2 connection using the app config."""
    return psycopg2.connect(
        current_app.config["DATABASE_URL"],
        cursor_factory=psycopg2.extras.RealDictCursor,
    )


def init_db():
    """Create tables if they do not already exist."""
    ddl = """
    CREATE TABLE IF NOT EXISTS users (
        id            SERIAL PRIMARY KEY,
        username      VARCHAR(80)  UNIQUE NOT NULL,
        email         VARCHAR(120) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        created_at    TIMESTAMP    DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id          SERIAL PRIMARY KEY,
        user_id     INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        title       VARCHAR(200) NOT NULL,
        description TEXT,
        priority    VARCHAR(10)  NOT NULL DEFAULT 'medium'
                        CHECK (priority IN ('low', 'medium', 'high')),
        status      VARCHAR(20)  NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending', 'in_progress', 'done')),
        created_at  TIMESTAMP    DEFAULT NOW()
    );
    """
    conn = get_conn()
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(ddl)
    finally:
        conn.close()
