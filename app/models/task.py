from .db import get_conn


class Task:
    def __init__(self, id, user_id, title, description, priority, status, created_at):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.priority = priority
        self.status = status
        self.created_at = created_at

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    @classmethod
    def get_all(cls, user_id, status=None, priority=None):
        filters = ["user_id = %s"]
        params = [user_id]
        if status:
            filters.append("status = %s")
            params.append(status)
        if priority:
            filters.append("priority = %s")
            params.append(priority)

        query = (
            "SELECT * FROM tasks WHERE "
            + " AND ".join(filters)
            + " ORDER BY created_at DESC"
        )
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
        finally:
            conn.close()
        return [cls(**row) for row in rows]

    @classmethod
    def get_by_id(cls, task_id, user_id):
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM tasks WHERE id = %s AND user_id = %s",
                    (task_id, user_id),
                )
                row = cur.fetchone()
        finally:
            conn.close()
        if row:
            return cls(**row)
        return None

    @classmethod
    def create(cls, user_id, title, description, priority, status):
        conn = get_conn()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO tasks (user_id, title, description, priority, status)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING *
                        """,
                        (user_id, title, description, priority, status),
                    )
                    row = cur.fetchone()
        finally:
            conn.close()
        return cls(**row)

    @classmethod
    def update(cls, task_id, user_id, **kwargs):
        allowed = {"title", "description", "priority", "status"}
        updates = {k: v for k, v in kwargs.items() if k in allowed and v is not None}
        if not updates:
            return cls.get_by_id(task_id, user_id)

        set_clause = ", ".join(f"{k} = %s" for k in updates)
        values = list(updates.values()) + [task_id, user_id]
        conn = get_conn()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        f"UPDATE tasks SET {set_clause} WHERE id = %s AND user_id = %s RETURNING *",
                        values,
                    )
                    row = cur.fetchone()
        finally:
            conn.close()
        if row:
            return cls(**row)
        return None

    @classmethod
    def delete(cls, task_id, user_id):
        conn = get_conn()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "DELETE FROM tasks WHERE id = %s AND user_id = %s RETURNING id",
                        (task_id, user_id),
                    )
                    row = cur.fetchone()
        finally:
            conn.close()
        return row is not None

    @classmethod
    def get_all_for_analytics(cls, user_id):
        """Return raw dicts for Pandas consumption."""
        conn = get_conn()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM tasks WHERE user_id = %s",
                    (user_id,),
                )
                rows = cur.fetchall()
        finally:
            conn.close()
        return [dict(row) for row in rows]
