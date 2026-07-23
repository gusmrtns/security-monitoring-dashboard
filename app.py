"""
app.py

Application factory. Usar create_app() em vez de uma instância global de
Flask facilita testes (cada teste pode criar sua própria app isolada) e
evita imports circulares entre blueprints e extensões.
"""

from flask import Flask, redirect, url_for

from config import Config
from extensions import db, login_manager, csrf


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from blueprints.auth.routes import auth_bp
    from blueprints.dashboard.routes import dashboard_bp
    from blueprints.findings.routes import findings_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(findings_bp, url_prefix="/findings")

    @app.route("/")
    def index():
        return redirect(url_for("dashboard.overview"))

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5000)
