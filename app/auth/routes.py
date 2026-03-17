from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..models import User


auth_bp = Blueprint("auth", __name__)

LANDING_RULES = [
    ("final_tables.view", "dashboard.final_tables"),
    ("data_sources.view", "dashboard.data_sources"),
    ("admin.users.view", "admin.users"),
    ("admin.roles.view", "admin.roles"),
    ("admin.departments.view", "admin.departments"),
    ("admin.permissions.view", "admin.permissions"),
]


def _resolve_landing_page(user: User) -> str:
    for permission_code, endpoint in LANDING_RULES:
        if user.has_permission(permission_code):
            return url_for(endpoint)
    return url_for("auth.login")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(_resolve_landing_page(current_user))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            next_url = request.args.get("next")
            if next_url:
                return redirect(next_url)
            return redirect(_resolve_landing_page(user))

        flash("用户名或密码错误", "error")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
