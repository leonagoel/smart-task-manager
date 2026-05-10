from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from app.models.user import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET"])
def register_page():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.dashboard"))
    return render_template("login.html")


@auth_bp.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not username or not email or not password:
        return jsonify({"error": "username, email and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    if User.get_by_email(email):
        return jsonify({"error": "Email already registered"}), 409
    if User.get_by_username(username):
        return jsonify({"error": "Username already taken"}), 409

    user = User.create(username, email, password)
    login_user(user, remember=True)
    return jsonify({"message": "Account created", "user_id": user.id, "username": user.username}), 201


@auth_bp.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.get_by_email(email)
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    login_user(user, remember=True)
    return jsonify({"message": "Logged in", "user_id": user.id, "username": user.username})


@auth_bp.route("/api/logout", methods=["POST"])
@login_required
def api_logout():
    logout_user()
    return jsonify({"message": "Logged out"}), 200