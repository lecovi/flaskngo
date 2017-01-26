"""
    flaskngo.auth
    ~~~~~~~~~~~~~~
    
    Authentication package
    
    :copyright: (c) 2016 by Leandro E. Colombo Viña <<@LeCoVi>>.
    :author: Leandro E. Colombo Viña <colomboleandro at bitson.com.ar>.
    :license: AGPL, see LICENSE for more details.
"""
# Standard lib imports
# Third-party imports
# BITSON imports
from .routes import auth


def init_auth():
    from .models import User, Role, RoleGroup, UserRole
    from app.constants import BITSON_DATE
    from app.extensions import db

    role_groups = [
        RoleGroup(id=0, name='N/A', description='N/A'),
        RoleGroup(name='admin', description='System administrators'),
        RoleGroup(name='user', description='Normal users'),
    ]

    roles = [
        Role(id=0, name='N/A', description='N/A', role_group_id=0),
        Role(name='root', description='Super Administrator', role_group_id=1),
        Role(name='user', description='User', role_group_id=2),
    ]

    users = [
        User(id=0, username='N/A', password_hash=None,
             email='no-reply@mail.com', active=False, confirmed=True,
             confirmed_at=BITSON_DATE, last_login_at=BITSON_DATE,
             last_login_ip='127.0.0.1', login_count=0)
    ]

    users[0].roles.append(roles[1])

    db.session.add_all(role_groups)
    db.session.add_all(roles)
    db.session.add_all(users)

    db.session.commit()


def init_demo_auth(count=10):
    from datetime import datetime
    from random import seed
    from sqlalchemy.exc import IntegrityError
    import forgery_py
    from .models import User, Role, RoleGroup, UserRole
    from app.extensions import db

    seed()
    r = Role.get_by(name='user')
    for i in range(count):
        u = User(username=forgery_py.internet.user_name(True),
                 email=forgery_py.internet.email_address(),
                 password='bitson',
                 active=True,
                 confirmed=True,
                 confirmed_at=datetime.now(),
                 )
        u.roles.append(r)
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
