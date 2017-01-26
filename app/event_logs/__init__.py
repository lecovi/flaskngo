"""
    flaskngo.event_logs
    ~~~~~~~~~~~~~~~~~~~~~~~
    
    Description
    
    :copyright: (c) 2016 by Leandro E. Colombo Viña <<@LeCoVi>>.
    :author: Leandro E. Colombo Viña <colomboleandro at bitson.com.ar>.
    :license: AGPL, see LICENSE for more details.
"""
# Standard lib imports
# Third-party imports
# BITSON imports


def init_event_logs():
    from app.extensions import db
    from .models import ActionGroup, Action, EventLog

    action_groups = [
        ActionGroup(id=0, description='N/A'),
        ActionGroup(description='HTTP methods'),
    ]

    actions = [
        Action(id=0, description='N/A', action_group_id=0),
        Action(description='Create', action_group_id=1),
        Action(description='Read', action_group_id=1),
        Action(description='Update', action_group_id=1),
        Action(description='Delete', action_group_id=1),
    ]

    event_logs = [
        EventLog(id=0, url='N/A', action_id=0, user_id=0, code_version='0.0.0'),
    ]

    db.session.add_all(action_groups)
    db.session.commit()

    db.session.add_all(actions)
    db.session.commit()

    db.session.add_all(event_logs)
    db.session.commit()


def init_demo_event_logs():
    pass
