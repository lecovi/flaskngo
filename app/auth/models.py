"""
    flaskngo.auth.models
    ~~~~~~~~~~~~~~~~~~~~~
    
    flaskngo SQLAlchemy Authentication models.
    
    :copyright: (c) 2016 by Leandro E. Colombo Viña <<@LeCoVi>>.
    :author: Leandro E. Colombo Viña <colomboleandro at bitson.com.ar>.
    :license: AGPL, see LICENSE for more details.
"""
# Standard lib imports
from datetime import datetime
# Third-party imports
from flask import g, current_app, request
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer,
                          BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_ctx
from sqlalchemy.dialects.postgresql import INET
# BITSON imports
from app.errors import unauthorized
from app.extensions import db, AppModel, httpauth


class Permission:
    READ = 0x01
    CREATE = 0x02
    MODIFY = 0x04
    DELETE = 0x08
    ADMINISTER = 0x80


class RoleGroup(AppModel):
    __tablename__ = 'auth_role_groups'

    name = db.Column(db.String(64), unique=True, index=True)
    roles = db.relationship('Role', back_populates='role_group')

    def export_data(self, exclude=None):
        response = super().export_data(exclude=exclude)
        roles = list()
        for role in self.roles:
            roles.append(role.export_data(exclude=exclude))
        response.update({'roles': roles})
        return response


class Role(AppModel):
    __tablename__ = 'auth_roles'

    name = db.Column(db.String(64), unique=True, index=True)
    role_group_id = db.Column(db.Integer, db.ForeignKey('auth_role_groups.id'))

    role_group = db.relationship('RoleGroup', back_populates='roles')

    @classmethod
    def create_with_role_group_name(cls, name, description, role_group_name):
        role_group = RoleGroup.get_by(name=role_group_name)
        new_role = cls(name=name, description=description,
                       role_group_id=role_group.id)
        db.session.add(new_role)
        db.session.commit()
        return new_role


class User(AppModel):
    __tablename__ = 'auth_users'

    description = None
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True, index=True)
    active = db.Column(db.Boolean, default=True)
    confirmed = db.Column(db.Boolean, default=False)
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(INET)
    login_count = db.Column(db.Integer, default=0)

    roles = db.relationship('Role', secondary='auth_users_roles',
                            backref=db.backref('users', lazy='dynamic'))

    @classmethod
    def create_with_role(cls, username, password, email, role, **kwargs):
        new_user = cls(username=username, password=password,
                       email=email, **kwargs)
        role = Role.get_by(name=role)
        new_user.roles.append(role)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = pwd_ctx.encrypt(password)

    def verify_password(self, password):
        return pwd_ctx.verify(password, self.password_hash)

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config.get('SECRET_KEY'),
                       expires_in=int(expiration))
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config.get('SECRET_KEY'))
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None  # valid token, but expired
        except BadSignature:
            return None  # invalid token
        user_id = data.get('id')
        if not user_id:
            return None
        return User.query.get(user_id)

    def generate_email_token(self, expiration):
        s = Serializer(current_app.config.get('SECRET_KEY'),
                       expires_in=int(expiration))
        return s.dumps({'email': self.email})

    @staticmethod
    def confirm(token):
        s = Serializer(current_app.config.get('SECRET_KEY'))
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        user = db.session.query(User).filter_by(email=data.get('email')).first()
        if not user or user.confirmed:
            return False
        user.confirmed = True
        user.confirmed_at = datetime.now()
        db.session.add(user)
        db.session.commit()
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config.get('SECRET_KEY'), int(expiration))
        return s.dumps({'reset': self.id})

    @staticmethod
    def verify_reset_password_token(token):
        s = Serializer(current_app.config.get('SECRET_KEY'))
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        return db.session.query(User).filter_by(id=data.get('reset')).first()

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config.get('SECRET_KEY'), int(expiration))
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    @staticmethod
    def change_email(token):
        s = Serializer(current_app.config.get('SECRET_KEY'))
        try:
            data = s.loads(token)
        except (BadSignature, SignatureExpired):
            return False
        user = db.session.query(User).filter_by(email=data.get(
            'new_email')).first()
        if not user or user.confirmed:
            return False
        user.confirmed = True
        user.confirmed_at = datetime.now()
        db.session.add(user)
        db.session.commit()
        return True

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def logged_in(self, commit=True):
        self.last_login_at = datetime.now()
        self.last_login_ip = request.remote_addr
        self.login_count += 1
        if commit:
            db.session.commit()

    def list_roles_names(self):
        return [role.name for role in self.roles]

    def add_role(self, role_name, commit=True):
        new_role = Role.get_by(name=role_name)
        if new_role:
            self.roles.append(new_role)
            if commit:
                db.session.commit()
            return True
        return False

    def remove_role(self, role_name, commit=True):
        if role_name not in self.list_roles_names():
            return False
        if len(self.roles) == 1:
            return False
        for i, role in enumerate(self.roles):
            if role.name == role_name:
                self.roles.pop(i)
                break
        if commit:
            db.session.commit()
        return True

    def export_data(self, exclude=None):
        response = super().export_data(exclude=exclude)
        roles = list()
        for role in self.roles:
            roles.append(role.export_data(exclude=exclude))
        response.update({'roles': roles})
        return response

    def set_active(self, commit=True):
        self.active = True
        if commit:
            db.session.commit()

    def set_inactive(self, commit=True):
        self.active = False
        if commit:
            db.session.commit()

    def set_confirmed(self, commit=True):
        self.confirmed = True
        if commit:
            db.session.commit()

    def set_not_confirmed(self, commit=True):
        self.confirmed = False
        if commit:
            db.session.commit()

    @classmethod
    def is_valid_username(cls, username):
        return User.get_by(username=username) is None

    @classmethod
    def is_valid_email(cls, email):
        return User.get_by(email=email) is None

    @classmethod
    def remove_fake(cls, item):
        max_user_role_id = UserRole.get_max_id()
        count = len(item.roles)
        super().remove_fake(item)
        UserRole.set_sequence_value(value=max_user_role_id - count)


class UserRole(AppModel):
    __tablename__ = 'auth_users_roles'

    description = None
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    role_id = db.Column(db.Integer, db.ForeignKey('auth_roles.id'))


@httpauth.verify_password
def verify_password(email_or_token=None, password=None):
    if current_app.config.get('AUTH_TOKEN_HEADER') in request.headers:
        token = request.headers.get(current_app.config.get('AUTH_TOKEN_HEADER'))
    elif request.json and current_app.config.get('AUTH_TOKEN_KEY') in request.json:
        token = request.json.get(current_app.config.get('AUTH_TOKEN_KEY'))
    else:
        return False
    g.current_user = User.verify_auth_token(token)
    if not g.current_user:
        return False
    if not g.current_user.active:
        return False
    if current_app.config.get('AUTH_CONFIRM_EMAIL') and not \
            g.current_user.confirmed:
        return False
    if g.current_user.erased:
        return False
    g.token_used = True
    return g.current_user is not None


@httpauth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')
