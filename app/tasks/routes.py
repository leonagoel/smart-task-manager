from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.models.task import Task
from app import socketio

tasks_bp = Blueprint("tasks", __name__)
dashboard_bp = Blueprint("dashboard", __name__)

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"pending", "in_progress", "done"}


# ── Dashboard (HTML) ───────────────────────────────────────────────────────────

@dashboard_bp.route("/")
@login_required
def dashboard():
    return render_template("index.html", user=current_user)


# ── GET all tasks ──────────────────────────────────────────────────────────────

@tasks_bp.route("/tasks", methods=["GET"])
@login_required
def get_tasks():
    status = request.args.get("status")
    priority = request.args.get("priority")
    tasks = Task.get_all(current_user.id, status=status, priority=priority)
    return jsonify([t.to_dict() for t in tasks])


# ── POST create task ───────────────────────────────────────────────────────────

@tasks_bp.route("/tasks", methods=["POST"])
@login_required
def create_task():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    priority = data.get("priority", "medium")
    status = data.get("status", "pending")

    if priority not in VALID_PRIORITIES:
        return jsonify({"error": f"priority must be one of {VALID_PRIORITIES}"}), 400
    if status not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of {VALID_STATUSES}"}), 400

    task = Task.create(
        user_id=current_user.id,
        title=title,
        description=data.get("description", ""),
        priority=priority,
        status=status,
    )
    task_dict = task.to_dict()

    # Broadcast real-time update via WebSocket
    socketio.emit("task_created", task_dict)

    return jsonify(task_dict), 201


# ── PUT update task ────────────────────────────────────────────────────────────

@tasks_bp.route("/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    data = request.get_json(silent=True) or {}

    priority = data.get("priority")
    status = data.get("status")

    if priority and priority not in VALID_PRIORITIES:
        return jsonify({"error": f"priority must be one of {VALID_PRIORITIES}"}), 400
    if status and status not in VALID_STATUSES:
        return jsonify({"error": f"status must be one of {VALID_STATUSES}"}), 400

    task = Task.update(
        task_id=task_id,
        user_id=current_user.id,
        title=data.get("title"),
        description=data.get("description"),
        priority=priority,
        status=status,
    )
    if not task:
        return jsonify({"error": "Task not found"}), 404

    task_dict = task.to_dict()
    socketio.emit("task_updated", task_dict)
    return jsonify(task_dict)


# ── DELETE task ────────────────────────────────────────────────────────────────

@tasks_bp.route("/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    deleted = Task.delete(task_id=task_id, user_id=current_user.id)
    if not deleted:
        return jsonify({"error": "Task not found"}), 404

    socketio.emit("task_deleted", {"id": task_id})
    return "", 204
