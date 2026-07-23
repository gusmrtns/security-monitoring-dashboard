"""
seed_data.py

Popula o banco com usuários de teste e ~100 achados de segurança
sintéticos, espalhados nos últimos 30 dias. Seed fixa (random.seed) para
reprodutibilidade - mesma prática usada no gerador de logs do Projeto 2.

Uso:
    python seed_data.py            # popula (mantém dados existentes)
    python seed_data.py --reset    # apaga tudo e recria do zero
"""

import argparse
import random
from datetime import timedelta

from app import create_app
from extensions import db, utcnow
from models.user import User
from models.finding import SecurityFinding, SEVERITY_CHOICES, CATEGORY_CHOICES, STATUS_CHOICES

random.seed(42)

MITRE_BY_CATEGORY = {
    "brute_force": "T1110",
    "user_enumeration": "T1087",
    "off_hours_access": None,
    "endpoint_scan": "T1595.002",
    "account_creation": "T1136.001",
    "malware_detection": "T1059.001",
    "data_exfiltration": "T1071",
}

TITLE_TEMPLATES = {
    "brute_force": "Possível força bruta a partir de {ip}",
    "user_enumeration": "Possível enumeração de usuários a partir de {ip}",
    "off_hours_access": "Login fora do horário comercial: usuário '{user}'",
    "endpoint_scan": "Varredura de endpoints sensíveis a partir de {ip}",
    "account_creation": "Conta de usuário criada: '{user}'",
    "malware_detection": "Execução suspeita de PowerShell detectada em {host}",
    "data_exfiltration": "Conexão de rede suspeita (possível C2) a partir de {host}",
}

DESCRIPTION_TEMPLATES = {
    "brute_force": "Múltiplas tentativas de autenticação falhas do IP {ip} em curto intervalo de tempo.",
    "user_enumeration": "O IP {ip} tentou autenticação com vários usuários distintos em sequência.",
    "off_hours_access": "Login bem-sucedido do usuário '{user}' fora da janela de horário comercial (7h-20h).",
    "endpoint_scan": "O IP {ip} gerou múltiplos erros HTTP contra caminhos sensíveis conhecidos (admin, .env, etc.).",
    "account_creation": "Nova conta '{user}' criada, requer revisão de legitimidade.",
    "malware_detection": "Processo PowerShell executado com argumentos codificados em Base64 no host {host}.",
    "data_exfiltration": "Conexão de rede persistente para IP externo incomum a partir do host {host}.",
}

SAMPLE_IPS = [
    "203.0.113.5", "198.51.100.9", "192.0.2.44", "203.0.113.77",
    "198.51.100.23", "192.168.1.15", "192.168.1.42", "10.0.0.8",
]
SAMPLE_USERS = ["root", "admin", "backup", "oracle", "postgres", "test", "carla", "gustavo", "svc_backup"]
SAMPLE_HOSTS = ["WIN10-AGENTE", "SRV-WEB01", "SRV-DB02", "DESKTOP-A31F9"]


def generate_finding(days_ago_max=30):
    category = random.choice(CATEGORY_CHOICES)
    ip = random.choice(SAMPLE_IPS)
    user = random.choice(SAMPLE_USERS)
    host = random.choice(SAMPLE_HOSTS)

    # Severidade correlacionada com a categoria (mais realista que puramente
    # aleatória): scans e força bruta tendem a Alta, off-hours tende a Média.
    if category in ("brute_force", "user_enumeration", "endpoint_scan", "account_creation"):
        severity = random.choices(SEVERITY_CHOICES, weights=[0.7, 0.25, 0.05])[0]
    elif category == "off_hours_access":
        severity = random.choices(SEVERITY_CHOICES, weights=[0.1, 0.7, 0.2])[0]
    else:
        severity = random.choices(SEVERITY_CHOICES, weights=[0.5, 0.35, 0.15])[0]

    timestamp = utcnow() - timedelta(
        days=random.randint(0, days_ago_max),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

    return SecurityFinding(
        timestamp=timestamp,
        severity=severity,
        category=category,
        title=TITLE_TEMPLATES[category].format(ip=ip, user=user, host=host),
        description=DESCRIPTION_TEMPLATES[category].format(ip=ip, user=user, host=host),
        source_ip=ip if category != "account_creation" or random.random() > 0.3 else None,
        mitre_technique=MITRE_BY_CATEGORY[category],
        status=random.choices(STATUS_CHOICES, weights=[0.5, 0.3, 0.2])[0],
    )


def seed(reset: bool = False, num_findings: int = 100):
    app = create_app()
    with app.app_context():
        if reset:
            db.drop_all()
        db.create_all()

        if not User.query.filter_by(username="admin").first():
            admin = User(username="admin", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)

        if not User.query.filter_by(username="analyst").first():
            analyst = User(username="analyst", role="analyst")
            analyst.set_password("analyst123")
            db.session.add(analyst)

        findings = [generate_finding() for _ in range(num_findings)]
        db.session.add_all(findings)
        db.session.commit()

        print(f"[+] Banco populado: {User.query.count()} usuário(s), {SecurityFinding.query.count()} achado(s).")
        print("[+] Login de teste: admin / admin123  ou  analyst / analyst123")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--reset", action="store_true", help="Apaga o banco existente antes de popular.")
    parser.add_argument("--count", type=int, default=100, help="Número de achados sintéticos a gerar.")
    args = parser.parse_args()

    seed(reset=args.reset, num_findings=args.count)
