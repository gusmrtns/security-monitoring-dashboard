"""
models/finding.py

Modelo central do dashboard: um achado de segurança. O vocabulário de
severidade e categorias segue o mesmo padrão usado no Projeto 2 (Log
Security Analyzer) - Alta/Média/Baixa e categorias como "brute_force",
"endpoint_scan" etc. - para manter os 3 projetos falando a mesma língua,
mesmo sem integração automática entre eles ainda.
"""

from extensions import db, utcnow

SEVERITY_CHOICES = ["Alta", "Média", "Baixa"]
STATUS_CHOICES = ["novo", "investigando", "resolvido"]

CATEGORY_CHOICES = [
    "brute_force",
    "user_enumeration",
    "off_hours_access",
    "endpoint_scan",
    "account_creation",
    "malware_detection",
    "data_exfiltration",
]


class SecurityFinding(db.Model):
    __tablename__ = "security_findings"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=utcnow, index=True)
    severity = db.Column(db.String(10), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    source_ip = db.Column(db.String(45))  # suporta IPv4 e IPv6
    mitre_technique = db.Column(db.String(20))
    status = db.Column(db.String(20), nullable=False, default="novo", index=True)

    def __repr__(self) -> str:
        return f"<Finding #{self.id} [{self.severity}] {self.title}>"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "source_ip": self.source_ip,
            "mitre_technique": self.mitre_technique,
            "status": self.status,
        }
