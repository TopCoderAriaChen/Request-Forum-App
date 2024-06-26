from exts import db
from datetime import datetime
from shortuuid import uuid
from enum import Enum
from werkzeug.security import generate_password_hash,check_password_hash


class PermissionEnum(Enum):
  BOARD = "BOARD"
  POST = "POST"
  COMMENT = "COMMENT"
  FRONT_USER = "FRONT_USER"
  CMS_USER = "CMS_USER"


class PermissionModel(db.Model):
  __tablename__ = "permission"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.Enum(PermissionEnum), nullable=False, unique=True)


role_permission_table = db.Table(
  "role_permission_table",
  db.Column("role_id", db.Integer, db.ForeignKey("role.id")),
  db.Column("permission_id", db.Integer, db.ForeignKey("permission.id"))
)

class RoleModel(db.Model):
  __tablename__ = 'role'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(50), nullable=False)
  desc = db.Column(db.String(200), nullable=True)
  create_time = db.Column(db.DateTime, default=datetime.now)

  permissions = db.relationship("PermissionModel", secondary=role_permission_table, backref="roles")


class UserModel(db.Model):
  __tablename__ = 'user'
  id = db.Column(db.String(100), primary_key=True, default=uuid)
  username = db.Column(db.String(50), nullable=False,unique=True)
  _password = db.Column(db.String(200), nullable=False)
  email = db.Column(db.String(50), nullable=False, unique=True)
  avatar = db.Column(db.String(100))
  signature = db.Column(db.String(100))
  join_time = db.Column(db.DateTime, default=datetime.now)
  is_staff = db.Column(db.Boolean, default=True)
  is_active = db.Column(db.Boolean,default=True)
  credit = db.Column(db.Integer, default=10)
  level = db.Column(db.Integer, default=1)

  # Foreign Key
  role_id = db.Column(db.Integer, db.ForeignKey("role.id"),default=1)
  role = db.relationship("RoleModel", backref="users")

  def __init__(self, *args, **kwargs):
    if "password" in kwargs:
      self.password = kwargs.get('password')
      kwargs.pop("password")
    super(UserModel, self).__init__(*args, **kwargs)

  @property
  def password(self):
    return self._password

  @password.setter
  def password(self, raw_password):
    self._password = generate_password_hash(raw_password)

  def check_password(self, raw_password):
    result = check_password_hash(self.password, raw_password)
    return result

  def has_permission(self, permission):
    return permission in [permission.name for permission in self.role.permissions] or permission=='POST'
  
  def add_credits(self, amount):
    """Increase the user's points"""
    self.credit += amount
    db.session.add(self)
    db.session.commit()