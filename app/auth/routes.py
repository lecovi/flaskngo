"""
    flaskngo.auth.routes
    ~~~~~~~~~~~~~~~~~~~~~
    
    Authentication views module.
    
    :copyright: (c) 2016 by Leandro E. Colombo Viña <<@LeCoVi>>.
    :author: Leandro E. Colombo Viña <colomboleandro at bitson.com.ar>.
    :license: AGPL, see LICENSE for more details.
"""
# Standard lib imports
# Third-party imports
from flask import Blueprint, request, jsonify, url_for, g, current_app
from sqlalchemy.exc import IntegrityError
# BITSON imports
from .decorators import roles_accepted, roles_required
from .models import User, Role, RoleGroup
from app.errors import unauthorized, bad_request, not_found
from app.extensions import db, httpauth
from app.email import celery_email


auth = Blueprint('auth', __name__, template_folder='templates/',
                 url_prefix='/auth')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    """ View function which handles logged_in.

        Using HTTP GET will send you instructions on how you have to logged_in.
        Using HTTP POST will handle logged_in request. First will try to
        load user using `email` provided, then the `username`.

        :param email: user email.
        :param password: user password.
        :param username: registered username.
        :returns: response in JSON format
    """
    if request.method == 'GET':
        response = {
            'data': {
                'url': url_for('.login', _external=True),
                'message': 'Send your username/email and password in a JSON '
                           'via POST to logged_in.',
            }
        }
        return jsonify(response)

    if request.method == 'POST':
        username = request.json.get('username')
        password = request.json.get('password')
        email = request.json.get('email')

        if not password and (not username or not email):
            return bad_request('Please send your credentials to logged_in')

        user = User.query.filter_by(email=email).first()
        if not user:
            user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            user.logged_in()
            g.current_user = user
        else:
            return unauthorized('Invalid credentials')

        token = user.generate_auth_token(current_app.config.get('SESSION_TTL'))
        response = {
            'data': {
                'token': token.decode('utf-8'),
                'expiration': current_app.config.get('SESSION_TTL'),
            }
        }
        return jsonify(response)


@auth.route('/register', methods=['POST'])
@roles_required('root')
def register():
    """ View function which handles users registration.

    :param username: registered username.
    :param password: user password.
    :param email: user email.
    :param role: role name for new user.
    :return: a JSON with user token & email confirmation URL.
    """
    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')
    role_name = request.json.get('role')
    if not username or not password or not email or not role_name:
        return bad_request('Invalid parameters')
    role = Role.get_by(name=role_name)
    if not role:
        return bad_request('Use a valid role please.')

    try:
        user = User(email=email, username=username, password=password,
                    login_count=0)
        user.roles.append(role)
        db.session.add(user)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return bad_request('Please use another username/email')
    expiration = current_app.config.get('SESSION_TTL')
    token = user.generate_auth_token(expiration=expiration)
    email_token = user.generate_email_token(expiration=expiration*5)
    celery_email(subject='Confirm Your Account', recipients=[user.email, ],
                 countdown=5, template='confirm_account',
                 username=username,
                 email_token=email_token.decode('utf-8'),
                 application=current_app.config.get('PROJECT_NAME').upper(),
                 )
    response = {
        'data': {
            'token': token.decode('utf-8'),
            'confirm_email_url': url_for('auth.confirm_email',
                                         email_token=email_token,
                                         _external=True),
            'expiration': expiration,
        }
    }
    current_app.logger.info('New user created %s', user)
    return jsonify(response), 201


@auth.route('/token')
@httpauth.login_required
def get_token():
    """ View function which returns a valid token for the user.

    :return: a JSON with user `token` & `expiration` value.
    """
    token = g.current_user.generate_auth_token(
        current_app.config.get('SESSION_TTL')
    )
    response = {
        'data': {
            'token': token.decode('utf-8'),
            'expiration': current_app.config.get('SESSION_TTL'),
        }
    }
    return jsonify(response)


@auth.route('/confirm/<email_token>')
def confirm_email(email_token):
    """
        View function which confirms user email.

    :param email_token: a valid token for the current user.
    :return: a JSON with a `message`.
    """
    if User.confirm(email_token):
        response = {
            'data': {
                'message': 'You have successfully confirmed your account!'
            }
        }
        return jsonify(response)
    else:
        return bad_request('The confirmation link is invalid or has expired.')


@auth.route('/send_confirm', methods=['POST'])
@httpauth.login_required
def send_confirmation_email():
    """
        View function which ask for confirmation email.

    :param email: user email.
    :param expiration: seconds until de token become invalid. Default value set
                       to `SESSION_TTL`.
    :return: a JSON with `email_confirmation_url` & `expiration` values.
    """
    email = request.get_json().get('email')
    expiration = request.get_json().get('expiration')
    if not expiration:
        expiration = current_app.config.get('SESSION_TTL')

    user = User.query.filter_by(email=email).first()
    if not user or not user.active:
        return bad_request('Ooops! Something went wrong!')
    if user.confirmed:
        return bad_request('User already confirmed')

    email_token = user.generate_email_token(expiration=expiration)

    celery_email(subject='Confirm Your Account', recipients=[user.email, ],
                 countdown=5, template='confirm_account',
                 username=user.username,
                 email_token=email_token.decode('utf-8'),
                 application=current_app.config.get('PROJECT_NAME').upper(),
                 )
    response = {
        'data': {
            'token': email_token.decode('utf-8'),
            'confirm_email_url': url_for('.confirm_email',
                                         email_token=email_token,
                                         _external=True),
            'expiration': expiration,
        }
    }
    return jsonify(response), 201


@auth.route('/change_email', methods=['POST'])
@httpauth.login_required
def change_email_request():
    """
        View function which handles the user change email request.

    :param new_email: new user email.
    :param expiration: seconds until de token become invalid. Default value set
                       to `SESSION_TTL`.
    :return: a JSON with `email_confirmation_url` & `expiration` values.
    """
    new_email = request.get_json().get('new_email')
    expiration = request.get_json().get('expiration')
    if not expiration:
        expiration = current_app.config.get('SESSION_TTL')

    user = User.get_by(email=new_email)
    if user:
        return bad_request('Ooops! Something went wrong!')
    if not expiration:
        expiration = current_app.config.get('SESSION_TTL')

    email_token = g.current_user.generate_email_change_token(
        new_email=new_email, expiration=expiration)
    g.current_user.confirmed = False
    g.current_user.email = new_email
    db.session.commit()
    celery_email(subject='Change email, reconfirm your account',
                 recipients=[g.current_user.email, ],
                 countdown=5, template='confirm_account_change_email',
                 username=g.current_user.username,
                 email_token=email_token.decode('utf-8'),
                 application=current_app.config.get('PROJECT_NAME').upper(),
                 )
    response = {
        'data': {
            'token': email_token.decode('utf-8'),
            'confirm_email_url': url_for('.change_email',
                                         email_token=email_token,
                                         _external=True),
            'expiration': expiration,
        }
    }
    return jsonify(response), 201


@auth.route('/change_email/<email_token>')
def change_email(email_token):
    """
        View function which handles user change of email.

    :param email_token: user valid email token.
    :return: a JSON with a `message`.
    """
    if User.change_email(email_token):
        response = {
            'data': {
                'message': 'You have successfully changed your email!'
            }
        }
        return jsonify(response)
    else:
        return bad_request('The confirmation link is invalid or has expired.')


@auth.route('/reset_password', methods=['POST'])
def reset_password_request():
    """
        View functions which handles user request to reset password.

        This function will first try to load the user using `email`, then will
        try with `username`.

    :param email: user email.
    :param username: registered username.
    :param expiration: seconds until de token become invalid. Default value set
                       to `SESSION_TTL`.
    :return: a JSON with token & expiration values.
    """
    email = request.get_json().get('email')
    username = request.get_json().get('username')
    expiration = request.get_json().get('expiration')
    if not email and not username:
        return bad_request('Please provide username/email.')

    if email:
        user = User.get_by(email=email)
    else:
        user = User.get_by(username=username)
    if not user or not user.active or user.erased:
        return bad_request('Please provide valid username/email.')

    if not expiration:
        expiration = current_app.config.get('SESSION_TTL')
    pwd_token = user.generate_reset_token(expiration=expiration)
    celery_email(subject='Reset your password',
                 recipients=[user.email, ],
                 countdown=5, template='reset_password',
                 username=user.username,
                 token=pwd_token.decode('utf-8'),
                 application=current_app.config.get('PROJECT_NAME').upper(),
                 )
    response = {
        'data': {
            'token': pwd_token.decode('utf-8'),
            'expiration': expiration,
        }
    }
    return jsonify(response)


@auth.route('/reset_password/<token>', methods=['GET'])
def reset_password(token):
    """
        View function which handles user password changes.

    :param token: a valid user token given by :func:`reset_password_request`.
    :return: a JSON with a `message`.
    """
    g.current_user = User.verify_reset_password_token(token=token)
    if not g.current_user:
        return bad_request('Invalid token')

    token = g.current_user.generate_auth_token(
        current_app.config.get('SESSION_TTL'))
    response = {
        'data': {
            'token': token.decode('utf-8'),
            'expiration': current_app.config.get('SESSION_TTL'),
            'url': url_for('.change_password', _external=True),
            'message': 'Send new password via JSON',
        }
    }
    return jsonify(response)


@auth.route('/change_password', methods=['POST'])
@httpauth.login_required
def change_password():
    new_password = request.get_json().get('new_password')
    if not new_password:
        return bad_request('Invalid password')
    g.current_user.password = new_password
    db.session.commit()
    response = {
        'data': {
            'message': 'You have successfully changed your password!'
        }
    }
    return jsonify(response)


def get_auth_table(table, exclude=None, erased=False):
    route = '.get_{}'.format(table.__tablename__.replace('auth_', ''))
    response = {
        'url': url_for(route, _external=True),
        'data': list()
    }
    results = db.session.query(table).filter_by(erased=erased).all()
    for result in results:
        response['data'].append(result.export_data(exclude=exclude))
    return response


def get_item(table, endpoint, item_id, exclude=None, erased=False):
    item = table.get_by(id=item_id, erased=erased)
    response = {
        'code': 200 if item else 404,
        'url': url_for(endpoint, item_id=item_id, _external=True),
        'data': item.export_data(exclude=exclude) if item else 'item not found'
    }
    return response


@auth.route('/role_groups/', methods=['GET'])
@httpauth.login_required
def get_role_groups():
    return jsonify(get_auth_table(table=RoleGroup))


@auth.route('/role_groups/<int:item_id>', methods=['GET'])
@httpauth.login_required
def get_role_group(item_id):
    response = get_item(table=RoleGroup, endpoint='.get_role_group',
                        item_id=item_id)
    return jsonify(response), response['code']


@auth.route('/role_groups/', methods=['POST'])
@roles_required('root')
def new_role_group():
    name = request.get_json().get('name')
    description = request.get_json().get('description')
    if not name or not description:
        return bad_request('Please provide name & description')
    try:
        new_item = RoleGroup(name=name, description=description)
        db.session.add(new_item)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return bad_request('Already in DB')
    response = {
        'data': {
            'url': url_for('.get_role_group', item_id=new_item.id,
                           _external=True),
        }
    }
    current_app.logger.info('New role group created %s', new_item)
    return jsonify(response), 201


@auth.route('/role_groups/<int:item_id>', methods=['PUT'])
@roles_required('root')
def edit_role_group(item_id):
    new_name = request.get_json().get('name')
    new_description = request.get_json().get('description')
    if not new_name or not new_description:
        return bad_request('Please provide new name or new description')

    role_group = RoleGroup.get_by(id=item_id)
    if not role_group:
        return not_found('item not found')

    try:
        role_group.name = new_name
        role_group.description = new_description
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return bad_request('already in DB')

    response = {
        'data': {
            'url': url_for('.get_role_group', item_id=role_group.id,
                           _external=True),
        }
    }
    return jsonify(response)


@auth.route('/role_groups/<int:item_id>', methods=['DELETE'])
@roles_required('root')
def delete_role_group(item_id):
    role_group = RoleGroup.get_by(id=item_id, erased=False)
    if not role_group:
        return not_found('item not found')
    role_group.set_erased()
    response = {
        'data': {
            'url': url_for('.delete_role_group', item_id=item_id, _external=True),
            'message': 'success',
        }
    }
    current_app.logger.info('Role group deleted %s', role_group)
    return jsonify(response), 204


@auth.route('/roles/', methods=['GET'])
@httpauth.login_required
def get_roles():
    return jsonify(get_auth_table(table=Role))


@auth.route('/roles/<int:item_id>', methods=['GET'])
@httpauth.login_required
def get_role(item_id):
    response = get_item(table=Role, endpoint='.get_role', item_id=item_id)
    return jsonify(response), response['code']


@auth.route('/roles/', methods=['POST'])
@roles_required('root')
def new_role():
    name = request.get_json().get('name')
    description = request.get_json().get('description')
    if not name or not description:
        return bad_request('Please provide name & description')

    role_group_id = request.get_json().get('role_group_id')
    role_group_name = request.get_json().get('role_group_name')
    if not role_group_id and not role_group_name:
        return bad_request('Please provide role group id or name')
    role_group = None
    if role_group_id:
        role_group = RoleGroup.get_by(id=role_group_id)
    elif role_group_name:
        role_group = RoleGroup.get_by(name=role_group_name)
    if not role_group:
        return bad_request('Please provide a valid role group id or name')

    try:
        new_item = Role(name=name, description=description)
        new_item.role_group = role_group
        db.session.add(new_item)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return bad_request('Already in DB')
    response = {
        'data': {
            'url': url_for('.get_role', item_id=new_item.id, _external=True),
            'message': 'created',
        }
    }
    current_app.logger.info('New role created %s', new_item)
    return jsonify(response), 201


@auth.route('/roles/<int:item_id>', methods=['PUT'])
@roles_required('root')
def edit_role(item_id):
    new_name = request.get_json().get('name')
    new_description = request.get_json().get('description')
    new_role_group_id = request.get_json().get('role_group_id')
    new_role_group_name = request.get_json().get('role_group_name')
    if not new_name and not new_description and \
            (not new_role_group_id or not new_role_group_name):
        return bad_request('Please provide new name or new description or '
                           'new role group id or name')
    role_group = None
    if new_role_group_id:
        role_group = RoleGroup.get_by(id=new_role_group_id)
    elif new_role_group_name:
        role_group = RoleGroup.get_by(name=new_role_group_name)
    if not role_group:
        return bad_request('Please provide a valid role group id or name')

    role = Role.get_by(id=item_id)
    if not role:
        return not_found('item not found')

    if Role.get_by(name=new_name):
        return bad_request('Already in DB')

    role.name = new_name
    role.description = new_description
    role.role_group = role_group
    db.session.add(role)
    db.session.commit()
    response = {
        'data': {
            'url': url_for('.get_role', item_id=item_id, _external=True),
            'message': 'modified',
        }
    }
    return jsonify(response)


@auth.route('/roles/<int:item_id>', methods=['DELETE'])
@roles_required('root')
def delete_role(item_id):
    role = Role.get_by(id=item_id)
    if not role:
        return not_found('item not found')
    role.set_erased()
    response = {
        'data': {
            'url': url_for('.delete_role', item_id=item_id, _external=True),
            'message': 'deleted',
        }
    }
    current_app.logger.info('Role deleted %s', role)
    return jsonify(response), 204


@auth.route('/users/', methods=['GET'])
@httpauth.login_required
def get_users():
    return jsonify(get_auth_table(table=User, exclude=['password_hash']))


@auth.route('/users/<int:item_id>', methods=['GET'])
@roles_required('root')
def get_user(item_id):
    return jsonify(get_item(table=User, item_id=item_id, endpoint='.get_user',
                            exclude=['password_hash'])
                   )


@auth.route('/users/', methods=['POST'])
@roles_required('root')
def new_user():
    response = {
        'data': {
            'url': url_for('.register', _external=True),
            'message': 'To create new users please use register URL'
        }
    }
    return jsonify(response)


@auth.route('/users/change_username', methods=['PUT'])
@httpauth.login_required
def change_my_username():
    new_username = request.get_json().get('username')
    if not new_username:
        return bad_request('Please provide username')
    if not User.is_valid_username(new_username):
        return bad_request('not valid username')

    g.current_user.username = new_username
    db.session.commit()

    response = {
        'data': {
            'message': 'updated',
        }
    }
    return jsonify(response)


@auth.route('/users/<int:item_id>/change_username', methods=['PUT'])
@roles_required('root')
def change_username(item_id):
    new_username = request.get_json().get('username')
    if not new_username:
        return bad_request('Please provide username')
    if not User.is_valid_username(new_username):
        return bad_request('not valid username')

    user = User.get_by(id=item_id)
    if not user:
        return not_found('item not found')
    user.username = new_username
    db.session.commit()

    response = {
        'data': {
            'message': 'updated',
        }
    }
    return jsonify(response)


@auth.route('/users/<int:item_id>', methods=['DELETE'])
@roles_required('root')
def delete_user(item_id):
    user = User.get_by(id=item_id)
    if not user:
        return not_found('item not found')
    user.set_erased()
    response = {
        'data': {
            'url': url_for('.delete_role', item_id=item_id, _external=True),
            'message': 'deleted',
        }
    }
    current_app.logger.info('User deleted %s', user)
    return jsonify(response), 204


@auth.route('/users/<int:item_id>/roles/<role_name>', methods=['POST'])
@roles_required('root')
def add_role_to_user(item_id, role_name):
    user = User.get_by(id=item_id)
    if not user:
        return not_found('user not found')
    if role_name in user.list_roles_names():
        return bad_request('user already has that role')
    if not user.add_role(role_name):
        return not_found('not valid role name')
    response = {
        'data': {
            'message': 'Role added to User.'
        }
    }
    return jsonify(response), 201


@auth.route('/users/<int:item_id>/roles/<role_name>', methods=['DELETE'])
@roles_required('root')
def remove_role_from_user(item_id, role_name):
    user = User.get_by(id=item_id)
    if not user:
        return not_found('user not found')
    if role_name not in user.list_roles_names():
        return bad_request('user does not has that role')
    if not user.remove_role(role_name):
        if len(user.roles) == 1:
            return bad_request('user only has that role! cannot be removed')
        else:
            return not_found('not valid role name')
    response = {
        'data': {
            'message': 'Role successfully removed from User.'
        }
    }
    return jsonify(response), 204


@auth.route('/users/<int:item_id>/active', methods=['PUT'])
@roles_required('root')
def activate_user(item_id):
    user = User.get_by(id=item_id)
    if not user:
        return not_found('user not found')
    user.set_active()
    response = {
        'data': {
            'message': 'User successfully activated.'
        }
    }
    current_app.logger.info('User activated %s', user)
    return jsonify(response)


@auth.route('/users/<int:item_id>/deactive', methods=['PUT'])
@roles_required('root')
def deactivate_user(item_id):
    user = User.get_by(id=item_id)
    if not user:
        return not_found('user not found')
    user.set_inactive()
    response = {
        'data': {
            'message': 'User successfully deactivated.'
        }
    }
    current_app.logger.info('User deactivated %s', user)
    return jsonify(response)


@auth.route('/roles_accepted', methods=['GET', 'POST'])
@roles_accepted('root')
def test_roles_accepted():
    """ View function to test logged_in.

    :return: a JSON with a `message`
    """
    response = {
        'data': {
            'message': 'Only root users are allowed! You are a member, welcome!'
        }
    }
    return jsonify(response)


@auth.route('/roles_required', methods=['GET', 'POST'])
@roles_required('root', 'normal')
def test_roles():
    """ View function to test logged_in.

    :return: a JSON with a `message`
    """
    response = {
        'data': {
            'message': 'Only root users are allowed! You are a member, welcome!'
        }
    }
    return jsonify(response)


@auth.route('/secret', methods=['GET', 'POST'])
@httpauth.login_required
def test_view():
    """ View function to test logged_in.

    :return: a JSON with a `message`
    """
    response = {
        'data': {
            'message': 'Only root users are allowed! You are a member, welcome!'
        }
    }
    return jsonify(response)
