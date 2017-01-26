"""
    flaskngo.main.routes
    ~~~~~~~~~~~~~~~~~~~~~
    
    Main domi routes module
    
    :copyright: (c) 2016 by Cooperativa de Trabajo BITSON Ltda..
    :author: Leandro E. Colombo Viña <colomboleandro at bitson.com.ar>.
    :license: AGPL, see LICENSE for more details.
"""
# Standard lib imports
# Third-party imports
from flask import Blueprint, url_for, jsonify, current_app, request, g
from flask_sqlalchemy import get_debug_queries
# BITSON imports
from ..event_logs.models import EventLog

main = Blueprint('main', __name__, template_folder='templates/')


@main.after_app_request
def after_request(response):
    if response.status_code in current_app.config.get('LOG_IN_DB').get(
            request.method) and not current_app.config['TESTING']:
        EventLog.register_http(
            url=request.base_url, method=request.method,
            user_id=0 if not g.current_user else g.current_user.id,
            params=request.get_json(), response=response,
            code_version=current_app.version,
        )
    for query in get_debug_queries():
        if query.duration >= current_app.config['SLOW_QUERY_TIMEOUT']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


@main.route('/')
def index():
    response = {
        'data': {
            'url': url_for('main.index', _external=True),
            'login': url_for('auth.login', _external=True),
            'message': 'You have to logged_in first',
            'about': url_for('main.about', _external=True),
        }
    }
    return jsonify(response)


@main.route('/about')
def about():
    response = {
        'data': {
            'url': url_for('main.about', _external=True),
            'version': current_app.version,
            'copyright': 'Leandro E. Colombo Viña <<@LeCoVi>>',
            'license': 'AGPL, see https://www.gnu.org/licenses/agpl-3.0.html '
                       'for more details.',
            'support': current_app.config.get['MAIL_ERROR_RECIPIENT'],
        }
    }
    return jsonify(response)
