"""
    config
    ~~~~~~

    Configuration module.

    :copyright: (c) 2016 by Cooperativa de Trabajo BITSON Ltda..
    :author: Leandro E. Colombo Viña <colomboleandro at bitson.com.ar>.
    :license: AGPL, see LICENSE for more details.
"""
# Standard lib imports
import os
# Third-party imports
from dotenv import load_dotenv
# BITSON imports

BASEDIR = os.path.dirname(os.path.abspath(__file__))

ENV_VARS = os.path.join(BASEDIR, ".env")
load_dotenv(ENV_VARS)


class Config:
    """Base config class"""
    PROJECT_NAME = os.environ.get('PROJECT_NAME')
    # SERVER_NAME = 'localhost:8000'
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SESSION_TTL = 3600

    AUTH_TOKEN_KEY = 'auth_token'
    AUTH_TOKEN_HEADER = 'Authentication-Token'
    AUTH_CONFIRM_EMAIL = True

    DOCKER_CONTAINER = '{}-db'.format(PROJECT_NAME)
    DB_SERVICE = os.environ.get('DB_SERVICE')
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')
    DB_URI = '{service}://{user}:{password}@{host}:{port}/{db}'.format(
        service=DB_SERVICE,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        db=DB_NAME
    )

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_SENDER')
    MAIL_SUBJECT_PREFIX = '[{}]'.format(PROJECT_NAME)
    MAIL_FLUSH_INTERVAL = 3600  # one hour
    MAIL_ERROR_RECIPIENT = os.environ.get('MAIL_ERROR_RECIPIENT')

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max payload to upload 16MB
    LOG_FOLDER = os.path.join(BASEDIR, 'logs')
    BACKUP_FOLDER = os.path.join(BASEDIR, 'backup')
    STATIC_FOLDER = os.path.join(BASEDIR, 'app', 'static')
    REPORT_FOLDER = os.path.join(STATIC_FOLDER, 'reports')
    UPLOAD_FOLDER = os.path.join(STATIC_FOLDER, 'uploads')
    IMAGES_FOLDER = os.path.join(UPLOAD_FOLDER, 'images')
    DEFAULTS_FOLDER = os.path.join(STATIC_FOLDER, 'defaults')
    DEFAULT_IMAGES_FOLDER = os.path.join(DEFAULTS_FOLDER, 'images')

    LOG_IN_DB = {
        'GET': [],
        'POST': [201, 200, 400],
        'PUT': [200, 400],
        'DELETE': [204, 400]
    }

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SLOW_QUERY_TIMEOUT = 0.5
    SQLALCHEMY_RECORD_QUERIES = False

    WTF_CSRF_ENABLED = False

    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERYD_LOG_FILE = os.path.join(LOG_FOLDER, 'celery.log')

    CELERYBEAT_SCHEDULE = {
        # 'total_members': {
        #     'task': 'sigas_sgs_back.reports.functions.update_total_members',
        #     'schedule': timedelta(seconds=5),
        #     # 'args': ()
        # },
    }

    CELERY_TIMEZONE = 'UTC'

    # MERCADOPAGO_CLIENT_ID = '273420415164856'
    # MERCADOPAGO_CLIENT_SECRET = 'IlsbHLB7USmY4W3xVIzIuPuuuZzDgKci'
    # MERCADOPAGO_PUBLIC_KEY = 'TEST-e7d197ef-b0df-404b-be49-fe9ddb4ffcb5'
    # MERCADOPAGO_ACCESS_TOKEN = 'TEST-273420415164856-070915-faf7b491c20f016597f2254ba8211daf__LB_LC__-162114602'

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SESSION_TTL = Config.SESSION_TTL * 4

    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DB_URL') or Config.DB_URI

    MAIL_FLUSH_INTERVAL = 60  # one minute


class TestingConfig(Config):
    DEBUG = False
    TESTING = True

    SERVER_NAME = os.environ.get('SERVER_NAME') or 'localhost'

    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DB_URL') or Config.DB_URI


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URL') or Config.DB_URI


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
