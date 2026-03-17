from sqlalchemy.exc import IntegrityError

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from ..extensions import db
from ..models import (
    Department,
    Permission,
    Role,
    SectorMaster,
    StrategyInsuranceMap,
    StrategyMaster,
    StrategySectorMap,
    User,
)
from ..permissions import permission_required


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/users")
@login_required
@permission_required("admin.users.view")
def users():
    items = User.query.order_by(User.id.desc()).all()
    return render_template("admin/users.html", items=items)


@admin_bp.route("/users/create", methods=["GET", "POST"])
@login_required
@permission_required("admin.users.view")
def create_user():
    roles = Role.query.order_by(Role.name.asc()).all()
    departments = Department.query.order_by(Department.name.asc()).all()

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        full_name = request.form.get("full_name", "").strip()
        email = request.form.get("email", "").strip() or None
        password = request.form.get("password", "")
        department_id = request.form.get("department_id")
        role_ids = request.form.getlist("role_ids")

        if not username or not full_name or not password:
            flash("用户名、用户姓名和密码是必填项", "error")
            return render_template(
                "admin/user_form.html",
                mode="create",
                user=None,
                roles=roles,
                departments=departments,
                selected_role_ids=set(),
            )

        user = User(username=username, full_name=full_name, email=email)
        user.set_password(password)

        if department_id:
            department = db.session.get(Department, int(department_id))
            user.department = department

        selected_roles = []
        for rid in role_ids:
            role = db.session.get(Role, int(rid))
            if role:
                selected_roles.append(role)
        user.roles = selected_roles

        db.session.add(user)
        try:
            db.session.commit()
            flash("用户创建成功", "success")
            return redirect(url_for("admin.users"))
        except IntegrityError:
            db.session.rollback()
            flash("用户名或邮箱已存在", "error")

    return render_template(
        "admin/user_form.html",
        mode="create",
        user=None,
        roles=roles,
        departments=departments,
        selected_role_ids=set(),
    )


@admin_bp.route("/users/<int:user_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("admin.users.view")
def edit_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        flash("用户不存在", "error")
        return redirect(url_for("admin.users"))

    roles = Role.query.order_by(Role.name.asc()).all()
    departments = Department.query.order_by(Department.name.asc()).all()

    if request.method == "POST":
        user.username = request.form.get("username", "").strip()
        user.full_name = request.form.get("full_name", "").strip()
        user.email = request.form.get("email", "").strip() or None
        user.is_active = request.form.get("is_active") == "on"

        password = request.form.get("password", "").strip()
        if password:
            user.set_password(password)

        department_id = request.form.get("department_id")
        user.department = db.session.get(Department, int(department_id)) if department_id else None

        role_ids = request.form.getlist("role_ids")
        selected_roles = []
        for rid in role_ids:
            role = db.session.get(Role, int(rid))
            if role:
                selected_roles.append(role)
        user.roles = selected_roles

        if not user.username or not user.full_name:
            flash("用户名和用户姓名不能为空", "error")
            return redirect(url_for("admin.edit_user", user_id=user_id))

        try:
            db.session.commit()
            flash("用户更新成功", "success")
            return redirect(url_for("admin.users"))
        except IntegrityError:
            db.session.rollback()
            flash("用户名或邮箱已存在", "error")

    return render_template(
        "admin/user_form.html",
        mode="edit",
        user=user,
        roles=roles,
        departments=departments,
        selected_role_ids={role.id for role in user.roles},
    )


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
@permission_required("admin.users.view")
def delete_user(user_id: int):
    user = db.session.get(User, user_id)
    if not user:
        flash("用户不存在", "error")
        return redirect(url_for("admin.users"))

    if user.username == "admin":
        flash("默认 admin 用户不允许删除", "error")
        return redirect(url_for("admin.users"))

    db.session.delete(user)
    db.session.commit()
    flash("用户已删除", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/roles")
@login_required
@permission_required("admin.roles.view")
def roles():
    items = Role.query.order_by(Role.id.desc()).all()
    return render_template("admin/roles.html", items=items)


@admin_bp.route("/roles/create", methods=["GET", "POST"])
@login_required
@permission_required("admin.roles.view")
def create_role():
    permissions = Permission.query.order_by(Permission.code.asc()).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None
        permission_ids = request.form.getlist("permission_ids")

        if not name:
            flash("角色名称不能为空", "error")
            return render_template(
                "admin/role_form.html",
                mode="create",
                role=None,
                permissions=permissions,
                selected_permission_ids=set(),
            )

        role = Role(name=name, description=description)
        selected_permissions = []
        for pid in permission_ids:
            p = db.session.get(Permission, int(pid))
            if p:
                selected_permissions.append(p)
        role.permissions = selected_permissions

        db.session.add(role)
        try:
            db.session.commit()
            flash("角色创建成功", "success")
            return redirect(url_for("admin.roles"))
        except IntegrityError:
            db.session.rollback()
            flash("角色名称已存在", "error")

    return render_template(
        "admin/role_form.html",
        mode="create",
        role=None,
        permissions=permissions,
        selected_permission_ids=set(),
    )


@admin_bp.route("/roles/<int:role_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("admin.roles.view")
def edit_role(role_id: int):
    role = db.session.get(Role, role_id)
    if not role:
        flash("角色不存在", "error")
        return redirect(url_for("admin.roles"))

    permissions = Permission.query.order_by(Permission.code.asc()).all()
    if request.method == "POST":
        role.name = request.form.get("name", "").strip()
        role.description = request.form.get("description", "").strip() or None
        permission_ids = request.form.getlist("permission_ids")

        if not role.name:
            flash("角色名称不能为空", "error")
            return redirect(url_for("admin.edit_role", role_id=role_id))

        selected_permissions = []
        for pid in permission_ids:
            p = db.session.get(Permission, int(pid))
            if p:
                selected_permissions.append(p)
        role.permissions = selected_permissions

        try:
            db.session.commit()
            flash("角色更新成功", "success")
            return redirect(url_for("admin.roles"))
        except IntegrityError:
            db.session.rollback()
            flash("角色名称已存在", "error")

    return render_template(
        "admin/role_form.html",
        mode="edit",
        role=role,
        permissions=permissions,
        selected_permission_ids={p.id for p in role.permissions},
    )


@admin_bp.route("/roles/<int:role_id>/delete", methods=["POST"])
@login_required
@permission_required("admin.roles.view")
def delete_role(role_id: int):
    role = db.session.get(Role, role_id)
    if not role:
        flash("角色不存在", "error")
        return redirect(url_for("admin.roles"))

    if role.name == "admin":
        flash("admin 角色不允许删除", "error")
        return redirect(url_for("admin.roles"))

    if role.users.count() > 0:
        flash("该角色已分配给用户，无法删除", "error")
        return redirect(url_for("admin.roles"))

    db.session.delete(role)
    db.session.commit()
    flash("角色已删除", "success")
    return redirect(url_for("admin.roles"))


@admin_bp.route("/departments")
@login_required
@permission_required("admin.departments.view")
def departments():
    items = Department.query.order_by(Department.id.desc()).all()
    return render_template("admin/departments.html", items=items)


@admin_bp.route("/departments/create", methods=["GET", "POST"])
@login_required
@permission_required("admin.departments.view")
def create_department():
    departments = Department.query.order_by(Department.name.asc()).all()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        code = request.form.get("code", "").strip()
        parent_id = request.form.get("parent_id")

        if not name or not code:
            flash("部门名和编码不能为空", "error")
            return render_template(
                "admin/department_form.html",
                mode="create",
                department=None,
                departments=departments,
            )

        department = Department(name=name, code=code)
        if parent_id:
            department.parent = db.session.get(Department, int(parent_id))

        db.session.add(department)
        try:
            db.session.commit()
            flash("部门创建成功", "success")
            return redirect(url_for("admin.departments"))
        except IntegrityError:
            db.session.rollback()
            flash("部门名或编码已存在", "error")

    return render_template(
        "admin/department_form.html",
        mode="create",
        department=None,
        departments=departments,
    )


@admin_bp.route("/departments/<int:department_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("admin.departments.view")
def edit_department(department_id: int):
    department = db.session.get(Department, department_id)
    if not department:
        flash("部门不存在", "error")
        return redirect(url_for("admin.departments"))

    departments = Department.query.order_by(Department.name.asc()).all()
    if request.method == "POST":
        department.name = request.form.get("name", "").strip()
        department.code = request.form.get("code", "").strip()

        parent_id = request.form.get("parent_id")
        if parent_id:
            parent = db.session.get(Department, int(parent_id))
            if parent and parent.id == department.id:
                flash("上级部门不能是自己", "error")
                return redirect(url_for("admin.edit_department", department_id=department_id))
            department.parent = parent
        else:
            department.parent = None

        if not department.name or not department.code:
            flash("部门名和编码不能为空", "error")
            return redirect(url_for("admin.edit_department", department_id=department_id))

        try:
            db.session.commit()
            flash("部门更新成功", "success")
            return redirect(url_for("admin.departments"))
        except IntegrityError:
            db.session.rollback()
            flash("部门名或编码已存在", "error")

    return render_template(
        "admin/department_form.html",
        mode="edit",
        department=department,
        departments=departments,
    )


@admin_bp.route("/departments/<int:department_id>/delete", methods=["POST"])
@login_required
@permission_required("admin.departments.view")
def delete_department(department_id: int):
    department = db.session.get(Department, department_id)
    if not department:
        flash("部门不存在", "error")
        return redirect(url_for("admin.departments"))

    if department.children:
        flash("该部门存在子部门，无法删除", "error")
        return redirect(url_for("admin.departments"))

    if department.users:
        flash("该部门存在用户，无法删除", "error")
        return redirect(url_for("admin.departments"))

    db.session.delete(department)
    db.session.commit()
    flash("部门已删除", "success")
    return redirect(url_for("admin.departments"))


@admin_bp.route("/permissions")
@login_required
@permission_required("admin.permissions.view")
def permissions():
    items = Permission.query.order_by(Permission.id.desc()).all()
    return render_template("admin/permissions.html", items=items)


@admin_bp.route("/permissions/create", methods=["GET", "POST"])
@login_required
@permission_required("admin.permissions.view")
def create_permission():
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip() or None

        if not code or not name:
            flash("权限代码和名称不能为空", "error")
            return render_template("admin/permission_form.html", mode="create", item=None)

        item = Permission(code=code, name=name, description=description)
        db.session.add(item)
        try:
            db.session.commit()
            flash("权限创建成功", "success")
            return redirect(url_for("admin.permissions"))
        except IntegrityError:
            db.session.rollback()
            flash("权限代码已存在", "error")

    return render_template("admin/permission_form.html", mode="create", item=None)


@admin_bp.route("/permissions/<int:permission_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("admin.permissions.view")
def edit_permission(permission_id: int):
    item = db.session.get(Permission, permission_id)
    if not item:
        flash("权限不存在", "error")
        return redirect(url_for("admin.permissions"))

    if request.method == "POST":
        item.code = request.form.get("code", "").strip()
        item.name = request.form.get("name", "").strip()
        item.description = request.form.get("description", "").strip() or None

        if not item.code or not item.name:
            flash("权限代码和名称不能为空", "error")
            return redirect(url_for("admin.edit_permission", permission_id=permission_id))

        try:
            db.session.commit()
            flash("权限更新成功", "success")
            return redirect(url_for("admin.permissions"))
        except IntegrityError:
            db.session.rollback()
            flash("权限代码已存在", "error")

    return render_template("admin/permission_form.html", mode="edit", item=item)


@admin_bp.route("/permissions/<int:permission_id>/delete", methods=["POST"])
@login_required
@permission_required("admin.permissions.view")
def delete_permission(permission_id: int):
    item = db.session.get(Permission, permission_id)
    if not item:
        flash("权限不存在", "error")
        return redirect(url_for("admin.permissions"))

    if item.roles.count() > 0:
        flash("该权限已分配给角色，无法删除", "error")
        return redirect(url_for("admin.permissions"))

    db.session.delete(item)
    db.session.commit()
    flash("权限已删除", "success")
    return redirect(url_for("admin.permissions"))


@admin_bp.route("/strategy-insurance-maps", methods=["GET", "POST"])
@login_required
@permission_required("admin.strategy_insurance_map.view")
def strategy_insurance_maps():
    strategies = StrategyMaster.query.order_by(StrategyMaster.strategy_no.asc()).all()

    if request.method == "POST":
        strategy = request.form.get("strategy", "").strip()
        insurance_type = request.form.get("insurance_type", "").strip()

        strategy_exists = StrategyMaster.query.filter_by(strategy_no=strategy).first()
        if not strategy or not strategy_exists or insurance_type not in {"投机", "套保"}:
            flash("策略和投保属性是必填项", "error")
            return redirect(url_for("admin.strategy_insurance_maps"))

        item = StrategyInsuranceMap(strategy=strategy, insurance_type=insurance_type)
        db.session.add(item)
        try:
            db.session.commit()
            flash("记录创建成功", "success")
        except IntegrityError:
            db.session.rollback()
            flash("策略已存在，请使用编辑", "error")
        return redirect(url_for("admin.strategy_insurance_maps"))

    items = StrategyInsuranceMap.query.order_by(StrategyInsuranceMap.id.desc()).all()
    return render_template("admin/strategy_insurance_maps.html", items=items, strategies=strategies)


@admin_bp.route("/strategy-insurance-maps/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("admin.strategy_insurance_map.view")
def edit_strategy_insurance_map(item_id: int):
    item = db.session.get(StrategyInsuranceMap, item_id)
    if not item:
        flash("记录不存在", "error")
        return redirect(url_for("admin.strategy_insurance_maps"))

    strategies = StrategyMaster.query.order_by(StrategyMaster.strategy_no.asc()).all()

    if request.method == "POST":
        strategy = request.form.get("strategy", "").strip()
        insurance_type = request.form.get("insurance_type", "").strip()
        strategy_exists = StrategyMaster.query.filter_by(strategy_no=strategy).first()
        if not strategy or not strategy_exists or insurance_type not in {"投机", "套保"}:
            flash("策略和投保属性是必填项", "error")
            return redirect(url_for("admin.edit_strategy_insurance_map", item_id=item_id))

        item.strategy = strategy
        item.insurance_type = insurance_type
        try:
            db.session.commit()
            flash("记录更新成功", "success")
            return redirect(url_for("admin.strategy_insurance_maps"))
        except IntegrityError:
            db.session.rollback()
            flash("策略已存在，请修改后再试", "error")

    return render_template("admin/strategy_insurance_map_form.html", item=item, strategies=strategies)


@admin_bp.route("/strategy-insurance-maps/<int:item_id>/delete", methods=["POST"])
@login_required
@permission_required("admin.strategy_insurance_map.view")
def delete_strategy_insurance_map(item_id: int):
    item = db.session.get(StrategyInsuranceMap, item_id)
    if not item:
        flash("记录不存在", "error")
        return redirect(url_for("admin.strategy_insurance_maps"))

    db.session.delete(item)
    db.session.commit()
    flash("记录已删除", "success")
    return redirect(url_for("admin.strategy_insurance_maps"))


@admin_bp.route("/strategy-sector-maps", methods=["GET", "POST"])
@login_required
@permission_required("admin.strategy_sector_map.view")
def strategy_sector_maps():
    strategies = StrategyMaster.query.order_by(StrategyMaster.strategy_no.asc()).all()
    sectors = SectorMaster.query.order_by(SectorMaster.name.asc()).all()

    if request.method == "POST":
        strategy = request.form.get("strategy", "").strip()
        sector = request.form.get("sector", "").strip()

        strategy_exists = StrategyMaster.query.filter_by(strategy_no=strategy).first()
        sector_exists = SectorMaster.query.filter_by(name=sector).first()
        if not strategy or not sector or not strategy_exists or not sector_exists:
            flash("策略和所属板块是必填项", "error")
            return redirect(url_for("admin.strategy_sector_maps"))

        item = StrategySectorMap(strategy=strategy, sector=sector)
        db.session.add(item)
        try:
            db.session.commit()
            flash("记录创建成功", "success")
        except IntegrityError:
            db.session.rollback()
            flash("策略已存在，请使用编辑", "error")
        return redirect(url_for("admin.strategy_sector_maps"))

    items = StrategySectorMap.query.order_by(StrategySectorMap.id.desc()).all()
    return render_template(
        "admin/strategy_sector_maps.html",
        items=items,
        strategies=strategies,
        sectors=sectors,
    )


@admin_bp.route("/strategy-sector-maps/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("admin.strategy_sector_map.view")
def edit_strategy_sector_map(item_id: int):
    item = db.session.get(StrategySectorMap, item_id)
    if not item:
        flash("记录不存在", "error")
        return redirect(url_for("admin.strategy_sector_maps"))

    strategies = StrategyMaster.query.order_by(StrategyMaster.strategy_no.asc()).all()
    sectors = SectorMaster.query.order_by(SectorMaster.name.asc()).all()

    if request.method == "POST":
        strategy = request.form.get("strategy", "").strip()
        sector = request.form.get("sector", "").strip()

        strategy_exists = StrategyMaster.query.filter_by(strategy_no=strategy).first()
        sector_exists = SectorMaster.query.filter_by(name=sector).first()
        if not strategy or not sector or not strategy_exists or not sector_exists:
            flash("策略和所属板块是必填项", "error")
            return redirect(url_for("admin.edit_strategy_sector_map", item_id=item_id))

        item.strategy = strategy
        item.sector = sector
        try:
            db.session.commit()
            flash("记录更新成功", "success")
            return redirect(url_for("admin.strategy_sector_maps"))
        except IntegrityError:
            db.session.rollback()
            flash("策略已存在，请修改后再试", "error")

    return render_template(
        "admin/strategy_sector_map_form.html",
        item=item,
        strategies=strategies,
        sectors=sectors,
    )


@admin_bp.route("/strategy-sector-maps/<int:item_id>/delete", methods=["POST"])
@login_required
@permission_required("admin.strategy_sector_map.view")
def delete_strategy_sector_map(item_id: int):
    item = db.session.get(StrategySectorMap, item_id)
    if not item:
        flash("记录不存在", "error")
        return redirect(url_for("admin.strategy_sector_maps"))

    db.session.delete(item)
    db.session.commit()
    flash("记录已删除", "success")
    return redirect(url_for("admin.strategy_sector_maps"))


@admin_bp.route("/sector-masters", methods=["GET", "POST"])
@login_required
@permission_required("admin.sector_master.view")
def sector_masters():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("板块名称不能为空", "error")
            return redirect(url_for("admin.sector_masters"))

        item = SectorMaster(name=name)
        db.session.add(item)
        try:
            db.session.commit()
            flash("板块创建成功", "success")
        except IntegrityError:
            db.session.rollback()
            flash("板块名称已存在", "error")
        return redirect(url_for("admin.sector_masters"))

    items = SectorMaster.query.order_by(SectorMaster.id.desc()).all()
    return render_template("admin/sector_masters.html", items=items)


@admin_bp.route("/sector-masters/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("admin.sector_master.view")
def edit_sector_master(item_id: int):
    item = db.session.get(SectorMaster, item_id)
    if not item:
        flash("记录不存在", "error")
        return redirect(url_for("admin.sector_masters"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("板块名称不能为空", "error")
            return redirect(url_for("admin.edit_sector_master", item_id=item_id))

        old_name = item.name
        item.name = name
        try:
            if old_name != name:
                StrategySectorMap.query.filter_by(sector=old_name).update(
                    {"sector": name}, synchronize_session=False
                )
            db.session.commit()
            flash("板块更新成功，关联表已同步", "success")
            return redirect(url_for("admin.sector_masters"))
        except IntegrityError:
            db.session.rollback()
            flash("板块名称已存在", "error")

    return render_template("admin/sector_master_form.html", item=item)


@admin_bp.route("/sector-masters/<int:item_id>/delete", methods=["POST"])
@login_required
@permission_required("admin.sector_master.view")
def delete_sector_master(item_id: int):
    item = db.session.get(SectorMaster, item_id)
    if not item:
        flash("记录不存在", "error")
        return redirect(url_for("admin.sector_masters"))

    linked_count = StrategySectorMap.query.filter_by(sector=item.name).count()
    if linked_count > 0:
        flash("该板块已在板块策略对应表中使用，不能删除", "error")
        return redirect(url_for("admin.sector_masters"))

    db.session.delete(item)
    db.session.commit()
    flash("板块已删除", "success")
    return redirect(url_for("admin.sector_masters"))


@admin_bp.route("/strategy-masters", methods=["GET", "POST"])
@login_required
@permission_required("admin.strategy_master.view")
def strategy_masters():
    if request.method == "POST":
        strategy_no = request.form.get("strategy_no", "").strip()
        if not strategy_no:
            flash("策略号不能为空", "error")
            return redirect(url_for("admin.strategy_masters"))

        item = StrategyMaster(strategy_no=strategy_no)
        db.session.add(item)
        try:
            db.session.commit()
            flash("策略创建成功", "success")
        except IntegrityError:
            db.session.rollback()
            flash("策略号已存在", "error")
        return redirect(url_for("admin.strategy_masters"))

    items = StrategyMaster.query.order_by(StrategyMaster.id.desc()).all()
    return render_template("admin/strategy_masters.html", items=items)


@admin_bp.route("/strategy-masters/<int:item_id>/edit", methods=["GET", "POST"])
@login_required
@permission_required("admin.strategy_master.view")
def edit_strategy_master(item_id: int):
    item = db.session.get(StrategyMaster, item_id)
    if not item:
        flash("记录不存在", "error")
        return redirect(url_for("admin.strategy_masters"))

    if request.method == "POST":
        strategy_no = request.form.get("strategy_no", "").strip()
        if not strategy_no:
            flash("策略号不能为空", "error")
            return redirect(url_for("admin.edit_strategy_master", item_id=item_id))

        old_strategy_no = item.strategy_no
        item.strategy_no = strategy_no
        try:
            if old_strategy_no != strategy_no:
                StrategyInsuranceMap.query.filter_by(strategy=old_strategy_no).update(
                    {"strategy": strategy_no}, synchronize_session=False
                )
                StrategySectorMap.query.filter_by(strategy=old_strategy_no).update(
                    {"strategy": strategy_no}, synchronize_session=False
                )
            db.session.commit()
            flash("策略更新成功，关联表已同步", "success")
            return redirect(url_for("admin.strategy_masters"))
        except IntegrityError:
            db.session.rollback()
            flash("策略号已存在", "error")

    return render_template("admin/strategy_master_form.html", item=item)


@admin_bp.route("/strategy-masters/<int:item_id>/delete", methods=["POST"])
@login_required
@permission_required("admin.strategy_master.view")
def delete_strategy_master(item_id: int):
    item = db.session.get(StrategyMaster, item_id)
    if not item:
        flash("记录不存在", "error")
        return redirect(url_for("admin.strategy_masters"))

    linked_insurance_count = StrategyInsuranceMap.query.filter_by(strategy=item.strategy_no).count()
    linked_sector_count = StrategySectorMap.query.filter_by(strategy=item.strategy_no).count()
    if linked_insurance_count > 0 or linked_sector_count > 0:
        flash("该策略已在对应表中使用，不能删除", "error")
        return redirect(url_for("admin.strategy_masters"))

    db.session.delete(item)
    db.session.commit()
    flash("策略已删除", "success")
    return redirect(url_for("admin.strategy_masters"))


@admin_bp.route("/change-password", methods=["GET", "POST"])
@login_required
@permission_required("account.change_password")
def change_password():
    if request.method == "POST":
        old_password = request.form.get("old_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not current_user.check_password(old_password):
            flash("原密码不正确", "error")
            return redirect(url_for("admin.change_password"))

        if len(new_password) < 8:
            flash("新密码长度至少 8 位", "error")
            return redirect(url_for("admin.change_password"))

        if new_password != confirm_password:
            flash("两次输入的新密码不一致", "error")
            return redirect(url_for("admin.change_password"))

        current_user.set_password(new_password)
        db.session.commit()
        flash("密码修改成功", "success")
        return redirect(url_for("admin.change_password"))

    return render_template("admin/change_password.html")
