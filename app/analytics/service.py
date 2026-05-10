import pandas as pd
import numpy as np


def compute_analytics(tasks_list: list[dict]) -> dict:
    """
    Accepts a list of task dicts from the DB and returns a stats dict
    computed with Pandas & NumPy.
    """
    if not tasks_list:
        return {
            "total": 0,
            "completed": 0,
            "pending": 0,
            "in_progress": 0,
            "completion_pct": 0.0,
            "by_priority": {"low": 0, "medium": 0, "high": 0},
            "by_status": {"pending": 0, "in_progress": 0, "done": 0},
            "daily_counts": [],
        }

    df = pd.DataFrame(tasks_list)

    # Ensure created_at is datetime
    df["created_at"] = pd.to_datetime(df["created_at"], utc=True)

    # Core counts
    total = int(len(df))
    completed = int(np.sum(df["status"] == "done"))
    pending = int(np.sum(df["status"] == "pending"))
    in_progress = int(np.sum(df["status"] == "in_progress"))

    # Completion percentage
    completion_pct = float(np.round((completed / total) * 100, 2)) if total else 0.0

    # Group by priority
    priority_counts = (
        df["priority"]
        .value_counts()
        .reindex(["low", "medium", "high"], fill_value=0)
        .to_dict()
    )
    priority_counts = {k: int(v) for k, v in priority_counts.items()}

    # Group by status
    status_counts = (
        df["status"]
        .value_counts()
        .reindex(["pending", "in_progress", "done"], fill_value=0)
        .to_dict()
    )
    status_counts = {k: int(v) for k, v in status_counts.items()}

    # Daily task creation trend (last 14 days)
    df["date"] = df["created_at"].dt.date
    daily = (
        df.groupby("date")
        .size()
        .reset_index(name="count")
        .tail(14)
    )
    daily_counts = [
        {"date": str(row["date"]), "count": int(row["count"])}
        for _, row in daily.iterrows()
    ]

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "in_progress": in_progress,
        "completion_pct": completion_pct,
        "by_priority": priority_counts,
        "by_status": status_counts,
        "daily_counts": daily_counts,
    }
