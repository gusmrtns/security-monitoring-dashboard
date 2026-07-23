"""
blueprints/dashboard/routes.py

A página principal renderiza o HTML "vazio" e o JS do lado do cliente
busca os dados dos gráficos via fetch() nos endpoints /api/charts/*.
Separar assim (em vez de montar os dados dentro do template Jinja) deixa
os mesmos endpoints reutilizáveis (ex: outra página, ou um consumidor
externo no futuro) e o JS de gráfico desacoplado da lógica de query.
"""

from datetime import timedelta

from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from sqlalchemy import func

from extensions import db, utcnow
from models.finding import SecurityFinding

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../../templates/dashboard")

DAYS_FOR_TIMELINE = 14


@dashboard_bp.route("/dashboard")
@login_required
def overview():
    total = SecurityFinding.query.count()
    open_count = SecurityFinding.query.filter(SecurityFinding.status != "resolvido").count()
    high_count = SecurityFinding.query.filter(SecurityFinding.severity == "Alta").count()

    latest = (
        SecurityFinding.query.order_by(SecurityFinding.timestamp.desc()).limit(5).all()
    )

    return render_template(
        "dashboard/index.html",
        total=total,
        open_count=open_count,
        high_count=high_count,
        latest=latest,
    )


@dashboard_bp.route("/api/charts/severity")
@login_required
def chart_severity():
    rows = (
        db.session.query(SecurityFinding.severity, func.count(SecurityFinding.id))
        .group_by(SecurityFinding.severity)
        .all()
    )
    counts = dict(rows)
    # Ordem fixa (Alta > Média > Baixa) em vez da ordem que o banco devolver,
    # pra o gráfico não "pular" a cada refresh.
    ordered = ["Alta", "Média", "Baixa"]
    return jsonify(
        labels=ordered,
        values=[counts.get(s, 0) for s in ordered],
    )


@dashboard_bp.route("/api/charts/categories")
@login_required
def chart_categories():
    rows = (
        db.session.query(SecurityFinding.category, func.count(SecurityFinding.id))
        .group_by(SecurityFinding.category)
        .order_by(func.count(SecurityFinding.id).desc())
        .all()
    )
    return jsonify(labels=[r[0] for r in rows], values=[r[1] for r in rows])


@dashboard_bp.route("/api/charts/timeline")
@login_required
def chart_timeline():
    since = utcnow() - timedelta(days=DAYS_FOR_TIMELINE)
    rows = (
        db.session.query(
            func.date(SecurityFinding.timestamp).label("day"),
            func.count(SecurityFinding.id),
        )
        .filter(SecurityFinding.timestamp >= since)
        .group_by("day")
        .order_by("day")
        .all()
    )
    counts_by_day = {r[0]: r[1] for r in rows}

    labels = []
    values = []
    for i in range(DAYS_FOR_TIMELINE, -1, -1):
        day = (utcnow() - timedelta(days=i)).strftime("%Y-%m-%d")
        labels.append(day)
        values.append(counts_by_day.get(day, 0))

    return jsonify(labels=labels, values=values)


@dashboard_bp.route("/api/charts/top-ips")
@login_required
def chart_top_ips():
    rows = (
        db.session.query(SecurityFinding.source_ip, func.count(SecurityFinding.id))
        .filter(SecurityFinding.source_ip.isnot(None))
        .group_by(SecurityFinding.source_ip)
        .order_by(func.count(SecurityFinding.id).desc())
        .limit(8)
        .all()
    )
    return jsonify(labels=[r[0] for r in rows], values=[r[1] for r in rows])
