from flask import Flask
from flask_login import LoginManager
from flask_socketio import SocketIO
from .models.db import init_db
from config import Config

socketio = SocketIO()
login_manager = LoginManager()


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )
    app.config.from_object(Config)

    # Extensions
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")

    # Init DB tables
    with app.app_context():
        init_db()

    # Blueprints
    from .auth.routes import auth_bp
    from .tasks.routes import tasks_bp, dashboard_bp
    from .analytics.routes import analytics_bp
    from .websocket.events import ws_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tasks_bp, url_prefix="/api")
    app.register_blueprint(analytics_bp, url_prefix="/api")
    app.register_blueprint(ws_bp)

    return app
