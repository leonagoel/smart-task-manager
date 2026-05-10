from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.models.task import Task
from .service import compute_analytics

analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/analytics", methods=["GET"])
@login_required
def get_analytics():
    tasks = Task.get_all_for_analytics(current_user.id)
    stats = compute_analytics(tasks)
    return jsonify(stats)
