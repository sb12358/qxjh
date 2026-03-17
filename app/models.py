from datetime import date, datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
)


role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id"), primary_key=True),
)


class TimestampMixin:
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Department(TimestampMixin, db.Model):
    __tablename__ = "departments"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    code = db.Column(db.String(50), unique=True, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)

    parent = db.relationship("Department", remote_side=[id], backref="children")


class Permission(TimestampMixin, db.Model):
    __tablename__ = "permissions"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)


class Role(TimestampMixin, db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    permissions = db.relationship(
        "Permission",
        secondary=role_permissions,
        lazy="joined",
        backref=db.backref("roles", lazy="dynamic"),
    )


class User(UserMixin, TimestampMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    full_name = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    department_id = db.Column(db.Integer, db.ForeignKey("departments.id"), nullable=True)

    department = db.relationship("Department", backref="users")
    roles = db.relationship(
        "Role",
        secondary=user_roles,
        lazy="joined",
        backref=db.backref("users", lazy="dynamic"),
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password, method="pbkdf2:sha256")

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    def has_permission(self, permission_code: str) -> bool:
        # 系统默认权限：每个用户都可以修改自己的密码
        if permission_code == "account.change_password":
            return True

        for role in self.roles:
            for permission in role.permissions:
                if permission.code == permission_code:
                    return True
        return False


class SourceTableConfig(TimestampMixin, db.Model):
    __tablename__ = "source_table_configs"

    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(120), unique=True, nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    owner_system = db.Column(db.String(120), nullable=True)
    description = db.Column(db.String(255), nullable=True)
    enabled = db.Column(db.Boolean, default=True)


class FinalTableConfig(TimestampMixin, db.Model):
    __tablename__ = "final_table_configs"

    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(120), unique=True, nullable=False)
    display_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    enabled = db.Column(db.Boolean, default=True)


class StrategyInsuranceMap(TimestampMixin, db.Model):
    __tablename__ = "strategy_insurance_maps"

    id = db.Column(db.Integer, primary_key=True)
    strategy = db.Column(db.String(120), unique=True, nullable=False)
    insurance_type = db.Column(db.String(20), nullable=False)


class StrategySectorMap(TimestampMixin, db.Model):
    __tablename__ = "strategy_sector_maps"

    id = db.Column(db.Integer, primary_key=True)
    strategy = db.Column(db.String(120), unique=True, nullable=False)
    sector = db.Column(db.String(120), nullable=False)


class SectorMaster(TimestampMixin, db.Model):
    __tablename__ = "sector_masters"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)


class StrategyMaster(TimestampMixin, db.Model):
    __tablename__ = "strategy_masters"

    id = db.Column(db.Integer, primary_key=True)
    strategy_no = db.Column(db.String(120), unique=True, nullable=False)


class SettlementFundBatch(TimestampMixin, db.Model):
    __tablename__ = "settlement_fund_batches"

    id = db.Column(db.Integer, primary_key=True)
    file_name = db.Column(db.String(255), nullable=False)
    sheet_name = db.Column(db.String(120), nullable=True)
    headers_json = db.Column(db.Text, nullable=False)
    row_count = db.Column(db.Integer, nullable=False, default=0)
    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)

    uploaded_by = db.relationship("User", backref="settlement_fund_batches")


class SettlementFundRecord(TimestampMixin, db.Model):
    __tablename__ = "settlement_fund_records"

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey("settlement_fund_batches.id"), nullable=False)
    row_no = db.Column(db.Integer, nullable=False)
    settlement_date = db.Column(db.Date, nullable=True, index=True)
    row_data = db.Column(db.JSON, nullable=False)

    batch = db.relationship(
        "SettlementFundBatch",
        backref=db.backref("records", lazy="dynamic", cascade="all, delete-orphan"),
    )


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))
