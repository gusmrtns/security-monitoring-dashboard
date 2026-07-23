"""
blueprints/findings/routes.py

Lista de achados com filtros combináveis via query string
(?severity=Alta&category=brute_force&q=203.0.113.5) e paginação.
Usar query string em vez de um form POST para filtrar deixa a URL
compartilhável/bookmarkável - útil num contexto de triagem de SOC.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required

from extensions import db
from models.finding import SecurityFinding, SEVERITY_CHOICES, CATEGORY_CHOICES, STATUS_CHOICES

findings_bp = Blueprint("findings", __name__, template_folder="../../templates/findings")


@findings_bp.route("/")
@login_required
def list_findings():
    query = SecurityFinding.query

    severity = request.args.get("severity", "")
    category = request.args.get("category", "")
    status = request.args.get("status", "")
    mitre = request.args.get("mitre", "").strip()
    search = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    if severity:
        query = query.filter(SecurityFinding.severity == severity)
    if category:
        query = query.filter(SecurityFinding.category == category)
    if status:
        query = query.filter(SecurityFinding.status == status)
    if mitre:
        query = query.filter(SecurityFinding.mitre_technique == mitre)
    if search:
        like_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                SecurityFinding.title.ilike(like_pattern),
                SecurityFinding.source_ip.ilike(like_pattern),
                SecurityFinding.description.ilike(like_pattern),
            )
        )

    query = query.order_by(SecurityFinding.timestamp.desc())

    per_page = current_app.config.get("FINDINGS_PER_PAGE", 15)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template(
        "findings/list.html",
        findings=pagination.items,
        pagination=pagination,
        severity_choices=SEVERITY_CHOICES,
        category_choices=CATEGORY_CHOICES,
        status_choices=STATUS_CHOICES,
        current_filters={
            "severity": severity,
            "category": category,
            "status": status,
            "mitre": mitre,
            "q": search,
        },
    )


@findings_bp.route("/<int:finding_id>")
@login_required
def detail(finding_id):
    finding = db.get_or_404(SecurityFinding, finding_id)
    return render_template("findings/detail.html", finding=finding, status_choices=STATUS_CHOICES)


@findings_bp.route("/<int:finding_id>/status", methods=["POST"])
@login_required
def update_status(finding_id):
    finding = db.get_or_404(SecurityFinding, finding_id)
    new_status = request.form.get("status")

    if new_status not in STATUS_CHOICES:
        flash("Status inválido.", "danger")
    else:
        finding.status = new_status
        db.session.commit()
        flash(f"Status do achado #{finding.id} atualizado para '{new_status}'.", "success")

    return redirect(url_for("findings.detail", finding_id=finding_id))
