from flask import Blueprint
from flask_socketio import emit
from flask_login import current_user
from app import socketio

ws_bp = Blueprint("ws", __name__)


@socketio.on("connect")
def handle_connect():
    if current_user.is_authenticated:
        emit("connected", {
            "message": f"Welcome {current_user.username}! Live updates are active.",
            "user_id": current_user.id,
        })
    else:
        emit("connected", {"message": "Connected (unauthenticated)"})


@socketio.on("disconnect")
def handle_disconnect():
    pass  # cleanup if needed


@socketio.on("ping_server")
def handle_ping(data):
    """Allow client to test the connection."""
    emit("pong_server", {"echo": data})
