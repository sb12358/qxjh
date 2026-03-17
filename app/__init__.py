from flask import Flask
from flask_migrate import Migrate
from sqlalchemy import inspect, text

from .config import Config
from .extensions import db, login_manager
from .models import Department, Permission, Role, User

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    from .admin.routes import admin_bp
    from .auth.routes import auth_bp
    from .dashboard.routes import dashboard_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(admin_bp)

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        inspector = inspect(db.engine)
        user_columns = {col["name"] for col in inspector.get_columns("users")}
        if "full_name" not in user_columns:
            db.session.execute(text("ALTER TABLE users ADD COLUMN full_name VARCHAR(80) NULL"))
            db.session.commit()

        record_columns = {col["name"] for col in inspector.get_columns("settlement_fund_records")}
        if "settlement_date" not in record_columns:
            db.session.execute(
                text("ALTER TABLE settlement_fund_records ADD COLUMN settlement_date DATE NULL")
            )
            db.session.execute(
                text(
                    "CREATE INDEX idx_settlement_fund_records_settlement_date "
                    "ON settlement_fund_records (settlement_date)"
                )
            )
            db.session.commit()

        # 将历史 JSON 数据中的结算日期回填到结构化字段，便于按日查询
        db.session.execute(
            text(
                "UPDATE settlement_fund_records "
                "SET settlement_date = STR_TO_DATE("
                "JSON_UNQUOTE(JSON_EXTRACT(row_data, '$.\"结算日期\"')), '%Y%m%d'"
                ") "
                "WHERE settlement_date IS NULL "
                "AND JSON_EXTRACT(row_data, '$.\"结算日期\"') IS NOT NULL"
            )
        )
        db.session.commit()
        print("Database tables created.")

    @app.cli.command("seed-demo")
    def seed_demo_command():
        # 权限名称统一采用“页面名称”规范，不使用“查看xx”前缀
        default_permissions = [
            ("dashboard.view", "首页总览"),
            ("data_sources.view", "导入源数据"),
            ("final_tables.view", "最终结果表"),
            ("admin.users.view", "用户管理"),
            ("admin.roles.view", "角色管理"),
            ("admin.departments.view", "组织架构"),
            ("admin.permissions.view", "权限配置"),
            ("admin.strategy_insurance_map.view", "策略投保属性对应表"),
            ("admin.strategy_sector_map.view", "板块策略对应表"),
            ("admin.sector_master.view", "板块维护"),
            ("admin.strategy_master.view", "策略维护"),
            ("account.change_password", "修改密码"),
        ]

        for code, name in default_permissions:
            exists = Permission.query.filter_by(code=code).first()
            if not exists:
                db.session.add(Permission(code=code, name=name))
            elif exists.name != name:
                exists.name = name

        dept = Department.query.filter_by(code="platform").first()
        if not dept:
            dept = Department(name="数据中台部", code="platform")
            db.session.add(dept)

        admin_role = Role.query.filter_by(name="admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="系统管理员")
            db.session.add(admin_role)

        viewer_role = Role.query.filter_by(name="viewer").first()
        if not viewer_role:
            viewer_role = Role(name="viewer", description="只读查看")
            db.session.add(viewer_role)

        db.session.commit()

        all_permissions = Permission.query.all()
        admin_role.permissions = all_permissions

        viewer_permissions = Permission.query.filter(
            Permission.code.in_(["dashboard.view", "data_sources.view", "final_tables.view"])
        ).all()
        viewer_role.permissions = viewer_permissions

        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                full_name="系统管理员",
                email="admin@company.com",
                department=dept,
            )
            admin_user.set_password("admin123")
            admin_user.roles.append(admin_role)
            db.session.add(admin_user)
        elif not admin_user.full_name:
            admin_user.full_name = "系统管理员"

        for u in User.query.all():
            if not u.full_name:
                u.full_name = u.username

        db.session.commit()
        print("Demo data seeded. default admin/admin123")

    @app.errorhandler(401)
    def unauthorized(_):
        return "未登录或登录状态已失效", 401

    @app.errorhandler(403)
    def forbidden(_):
        return "你没有访问此页面的权限", 403

    return app
