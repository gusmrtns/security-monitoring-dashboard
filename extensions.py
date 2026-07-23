"""
extensions.py

Instâncias de extensões Flask criadas aqui, SEM vínculo com a app ainda
(vínculo acontece em app.py via .init_app()). Esse padrão evita imports
circulares: models.py e blueprints podem importar `db` e `login_manager`
daqui sem precisar importar app.py, que por sua vez importa os blueprints.
"""

from datetime import datetime, timezone

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf import CSRFProtect

db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = "Faça login para acessar o dashboard."
login_manager.login_message_category = "info"


def utcnow() -> datetime:
    """
    UTC "naive" (sem tzinfo), para armazenar em SQLite de forma consistente.
    datetime.utcnow() está deprecado desde o Python 3.12 - este helper usa a
    API recomendada (datetime.now(timezone.utc)) e remove o tzinfo depois,
    mantendo o mesmo formato que já era usado no banco.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
