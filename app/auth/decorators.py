"""
    flaskngo.auth.decorators
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Authentication decorators.
    
    :copyright: (c) 2016 by Leandro E. Colombo Viña <<@LeCoVi>>.
    :author: Leandro E. Colombo Viña <colomboleandro at bitson.com.ar>.
    :license: AGPL, see LICENSE for more details.
"""
# Standard lib imports
from functools import wraps
# Third-party imports
from flask import g
# BITSON imports
from .models import verify_password
from app.errors import unauthorized, forbidden


def roles_required(*roles):
    """Decorator which specifies that a user must have all the specified roles.
    Example::

        @app.route('/data')
        @roles_required('admin', 'analyst')
        def data():
            return 'awesome data'

    The logged user must have both the `admin` role and `analyst` role in order
    to view the page

    :param roles: The required roles
    """

    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if verify_password():
                for role in roles:
                    if role not in g.current_user.list_roles_names():
                        return forbidden('Not enough permissions')
                return fn(*args, **kwargs)
            else:
                return unauthorized('Invalid credentials')
        return decorated_view
    return wrapper


def roles_accepted(*roles):
    """Decorator which specifies that a user must have at least one of the
    specified roles.
    Example::

        @app.route('/data')
        @roles_accepted('admin', 'editor')
        def edit_data():
            return 'data modified'

    The logged user must have either the `admin` role or the `editor` role in
    order to view the page

    :param roles: The possible roles
    """

    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if verify_password():
                for role in roles:
                    if role in g.current_user.list_roles_names():
                        return fn(*args, **kwargs)
                return forbidden('Not enough permissions')
            else:
                return unauthorized('Invalid Credentials')
        return decorated_view
    return wrapper
