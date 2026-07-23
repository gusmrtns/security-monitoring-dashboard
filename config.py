"""
config.py

Configuração da aplicação Flask. Mantido simples de propósito: uma única
classe Config, sem separação Dev/Prod/Test por enquanto (projeto é para
portfólio de curto prazo - complexidade extra fica pra fase de melhorias).
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    # Em produção real isso viria de variável de ambiente. Para um projeto
    # de portfólio local, um valor fixo + aviso no README é suficiente e
    # mais simples de rodar para quem clonar o repositório.
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-troque-em-producao")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'security_dashboard.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Quantos achados exibir por página na listagem (findings)
    FINDINGS_PER_PAGE = 15
