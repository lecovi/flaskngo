"""
    FLASKNGO BACKEND
    ~~~~~~~~~~~~

    Flaskngo main backend app.

    :copyright: (c) 2016 by Leandro E. Colombo Viña <<@LeCoVi>>.
    :author: Leandro E. Colombo Viña & Alejandro Brunacci.
    :license: GPL v3.0, see LICENSE for more details.

"""
# Standard Lib imports
import os
import logging
import time
from logging.handlers import RotatingFileHandler
import datetime
# Third-party imports
from flask import Flask
# from flask_restless import APIManager
# BITSON imports
from .auth import auth as auth_blueprint
from .main import main as main_blueprint
# FIXME: include EventLog into restless to log modifications.
from .event_logs.models import EventLog  # needed to include in migrations.
from .errors import CUSTOM_ERRORS, CustomErrors, add_method
from .extensions import celery, cors, db, mail, migrate
from .helpers import register_apis, register_blueprints, create_folders

from config import config, Config

# For import *
__all__ = ['create_app']
__version__ = '1.0.0'

BLUEPRINTS = [
    auth_blueprint,
    main_blueprint,
    ]

MODELS = [
    ]


def create_app(config_name):
    app = Flask(__name__, static_url_path='')
    app.config.from_object(config[config_name])
    app.version = __version__

    create_folders(app=app)

    celery.conf.update(app.config)

    if not app.debug and not app.config['TESTING']:
        # configure logging for production
        pass

    log_format = "".join(["[%(asctime)s] %(name)20s - %(levelname)8s: ",
                          "%(threadName)15s-%(funcName)15s() - %(message)s"])
    formatter = logging.Formatter(fmt=log_format)
    # Format UTC Time
    formatter.converter = time.gmtime
    logfile = os.path.join(Config.LOG_FOLDER,
                           '{}.log'.format(Config.PROJECT_NAME))

    fh = logging.handlers.RotatingFileHandler(filename=logfile,
                                              maxBytes=10e6,
                                              backupCount=10)
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    app.logger.addHandler(fh)

    db.init_app(app)
    mail.init_app(app)
    # login_manager.session_protection = 'strong'
    # login_manager.login_view = 'auth.logged_in'
    # login_manager.init_app(app)

    with app.app_context():
        migrate.init_app(app, db)
        # manager = APIManager(flask_sqlalchemy_db=db)

        register_blueprints(app=app, blueprints=BLUEPRINTS)
        # register_apis(apimanager=manager, apis=MODELS, url_prefix=URL_PREFIX)

        # manager.init_app(app)
        cors.init_app(app)

        app.jinja_env.globals.update(datetime=datetime)

        for error_code in CUSTOM_ERRORS:
            add_method(CustomErrors, app, error_code)

    return app
