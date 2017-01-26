"""
    flaskngo.event_logs.models
    ~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Description
    
    :copyright: (c) 2016 by Leandro E. Colombo Viña <<@LeCoVi>>.
    :author: Leandro E. Colombo Viña <colomboleandro at bitson.com.ar>.
    :license: AGPL, see LICENSE for more details.
"""
# Standard lib imports
import json
from datetime import datetime
# Third-party imports
from sqlalchemy.dialects.postgresql import JSON
# BITSON imports
from app.extensions import db, AppModel


class ActionGroup(AppModel):
    __tablename__ = 'action_groups'


class Action(AppModel):
    __tablename__ = 'actions'

    action_group_id = db.Column(db.Integer,
                                db.ForeignKey('action_groups.id'), default=0)


class EventLog(db.Model):
    __tablename__ = 'event_logs'
    HTTP_METHODS = {
        'POST': 1,
        'GET': 2,
        'PUT': 3,
        'DELETE': 4,
    }

    id = db.Column(db.Integer, primary_key=True, index=True)
    url = db.Column(db.String(), nullable=False, index=True)
    action_id = db.Column(db.Integer, db.ForeignKey('actions.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('auth_users.id'))
    params = db.Column(JSON)
    response = db.Column(JSON)
    code_version = db.Column(db.String(15), nullable=False, index=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @classmethod
    def register_http(cls, method, response, **kwargs):
        action_id = cls.HTTP_METHODS[method]
        rd = {
            'status code': response.status_code,
            'status': response.status,
            'headers': dict((k, v) for k, v in response.headers.to_list()),
            'response values': json.loads(response.get_data('utf-8')),
        }
        event = cls(action_id=action_id, response=rd, **kwargs)

        db.session.add(event)
        db.session.commit()
