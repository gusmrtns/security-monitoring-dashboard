"""
tests/test_routes.py

Testes de integração das rotas, usando SQLite em memória (config isolada
da app "de verdade" - nunca toca em security_dashboard.db).
Rodar com: pytest -v
"""

import pytest

from app import create_app
from config import Config
from extensions import db
from models.user import User
from models.finding import SecurityFinding


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False  # simplifica os testes de POST; a proteção real é coberta à parte


@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        user = User(username="tester", role="analyst")
        user.set_password("senha123")
        db.session.add(user)
        db.session.commit()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username="tester", password="senha123"):
    return client.post("/auth/login", data={"username": username, "password": password}, follow_redirects=True)


class TestAuth:
    def test_dashboard_requires_login(self, client):
        response = client.get("/dashboard", follow_redirects=True)
        assert "Faça login".encode("utf-8") in response.data or response.request.path == "/auth/login"

    def test_login_with_valid_credentials_succeeds(self, client):
        response = login(client)
        assert response.status_code == 200
        assert response.request.path == "/dashboard"

    def test_login_with_invalid_password_fails(self, client):
        response = client.post(
            "/auth/login", data={"username": "tester", "password": "senha-errada"}, follow_redirects=True
        )
        assert "usu\u00e1rio ou senha inv\u00e1lidos".encode("utf-8") in response.data.lower() or response.status_code == 200
        assert response.request.path == "/auth/login"

    def test_logout_redirects_to_login(self, client):
        login(client)
        response = client.get("/auth/logout", follow_redirects=True)
        assert response.request.path == "/auth/login"


class TestFindings:
    def _create_finding(self, app, **overrides):
        with app.app_context():
            defaults = dict(
                severity="Alta",
                category="brute_force",
                title="Teste de força bruta",
                description="descrição de teste",
                source_ip="203.0.113.5",
                mitre_technique="T1110",
                status="novo",
            )
            defaults.update(overrides)
            finding = SecurityFinding(**defaults)
            db.session.add(finding)
            db.session.commit()
            return finding.id

    def test_list_requires_login(self, client):
        response = client.get("/findings/", follow_redirects=True)
        assert response.request.path == "/auth/login"

    def test_list_shows_seeded_finding(self, app, client):
        self._create_finding(app, title="Achado único de teste")
        login(client)
        response = client.get("/findings/")
        assert b"Achado \xc3\xbanico de teste" in response.data

    def test_filter_by_severity_excludes_other_severities(self, app, client):
        self._create_finding(app, severity="Alta", title="Achado Alta")
        self._create_finding(app, severity="Baixa", title="Achado Baixa")
        login(client)

        response = client.get("/findings/?severity=Alta")
        assert b"Achado Alta" in response.data
        assert b"Achado Baixa" not in response.data

    def test_update_status_changes_value(self, app, client):
        finding_id = self._create_finding(app, status="novo")
        login(client)

        client.post(f"/findings/{finding_id}/status", data={"status": "resolvido"}, follow_redirects=True)

        with app.app_context():
            finding = db.session.get(SecurityFinding, finding_id)
            assert finding.status == "resolvido"

    def test_detail_page_returns_404_for_missing_finding(self, client):
        login(client)
        response = client.get("/findings/9999")
        assert response.status_code == 404
