#!/usr/bin/env python

# Standard Lib imports
import os
# Third-party imports
from flask_migrate import MigrateCommand
from flask_script import Manager
# BITSON imports
from app import create_app
from app.logger import console_logger

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

manager = Manager(app)
manager.add_command('db', MigrateCommand)


@manager.command
def createsuperuser(default=False):
    """Creates superuser."""
    from datetime import datetime
    from getpass import getpass
    from sqlalchemy.exc import IntegrityError
    from app.auth.models import User

    if default:
        console_logger.warn("Creating default superuser...")
        User.create_with_role(username='bitson', password='bitson', role='root',
                              email='info@bitson.com.ar', confirmed=True,
                              confirmed_at=datetime.now())
        return

    try:
        username = input('\033[34mPlease enter superuser username: \033[0m')
        email = input('\033[34mPlease enter superuser email: \033[0m')
        password = getpass(prompt='\033[34mPassword: \033[0m')
        password_confirm = getpass(prompt='\033[34mConfirm password: \033[0m')
        if password != password_confirm:
            console_logger.error("Password doesn't match")
            return

        User.create_with_role(username=username, password=password,
                              role='root', email=email, confirmed=True,
                              confirmed_at=datetime.now())

        console_logger.debug("Done!")
    except KeyboardInterrupt:
        console_logger.error("\nCtrl-C detected: Abort by user")
    except IntegrityError as error:
        console_logger.critical(error)


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    # If FLASK_COVERAGE environment variable is not set, set it and restart.
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        # Integrating code coverage with the manage.py script presents a
        # small problem. By the time the --coverage option is received in the
        # test() function, it is already too late to turn on coverage metrics;
        # by that time all the code in the global scope has already executed.
        # To get accurate metrics, the script restarts itself after setting the
        # FLASK_COVERAGE environment variable. In the second run, the top of
        # the script finds that the environment variable is set and turns on
        # coverage from the start.
        import sys
        console_logger.warning("Coverage detected... relaunching")
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)

    import unittest

    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

    if COV:
        from config import BASEDIR, Config
        COV.stop()
        COV.save()
        console_logger.debug('Coverage Summary:')
        COV.report()
        coverage_dir = os.path.join(BASEDIR, Config.LOG_FOLDER, 'coverage')
        COV.html_report(directory=coverage_dir)
        console_logger.debug(
            'HTML version: file://{}/index.html'.format(coverage_dir)
        )
        COV.erase()


@manager.command
def profile(length=25):
    """ Start the application under the code profiler. """
    from werkzeug.contrib.profiler import ProfilerMiddleware
    from config import BASEDIR, Config

    profile_dir = os.path.join(BASEDIR, Config.LOG_FOLDER, 'profile')
    console_logger.debug(" * Running app with profiler!")
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def make_docs(builder='html', verbose=False, show=False):
    """Creates documentation based on RST files."""
    from config import BASEDIR
    from subprocess import Popen, STDOUT, PIPE

    docs_folder = os.path.join(BASEDIR, 'docs')
    static_docs_folder = os.path.join(docs_folder, '_static')
    if not os.path.isdir(static_docs_folder):
        os.mkdir(static_docs_folder)

    cmd = "make {}".format(builder)
    proc = Popen(cmd, cwd=docs_folder, shell=True, stdout=PIPE, stderr=STDOUT)

    stdout_value, stderr_value = proc.communicate()
    if verbose:
        console_logger.debug('\nOUTPUT: ')
        console_logger.info(stdout_value.decode())
        if stderr_value:
            console_logger.warning('\nERROR: ')
            console_logger.warning(stderr_value.decode())

    if show:
        separator = 'Build finished. The HTML pages are in '
        build_html = stdout_value.decode().partition(separator)[-1]
        build_html = build_html.strip('.\n')
        index_path = os.path.join(docs_folder, build_html, 'index.html')
        open_index = 'xdg-open {}'.format(index_path)
        Popen(open_index, shell=True)


@manager.command
def new_package(name=None, description=None):
    """Creates new package from templates."""
    from datetime import date
    from subprocess import check_output
    from jinja2 import Environment, PackageLoader, select_autoescape
    from config import BASEDIR

    app_dir = os.path.join(BASEDIR, 'app')
    templates_dir = os.path.join(app_dir, 'templates', 'pkg')

    if not name:
        name = input('\033[1;37mPackage name: \033[0m')
        name = name.lower()

    msg = check_output(['git', 'flow', 'feature', 'start', name])

    package_path = os.path.join(app_dir, name)
    if os.path.isdir(package_path):
        console_logger.critical('ERROR: package %s already exists', name)
        return
    else:
        os.mkdir(package_path)

    if not description:
        description = input('\033[1;37mShort description: \033[0m')
    year = date.today().year
    author = check_output(['git', 'config', 'user.name']).decode().strip()
    mail_user = check_output(
        ['git', 'config', 'user.email']).decode().split('@')[0].strip()

    env = Environment(loader=PackageLoader('app', 'templates/pkg'),
                      autoescape=select_autoescape(['html', 'xml'])
                      )

    items = os.listdir(templates_dir)
    for item in items:
        if os.path.isfile(os.path.join(templates_dir, item)) and '.tmpl' in \
                item:
            template = env.get_template(item)
            rendered = template.render(package_name=name, year=year,
                                       author=author, mail_user=mail_user,
                                       description=description)
            filename, _ = item.split('.tmpl')
            with open(os.path.join(package_path, filename), 'w') as python_file:
                python_file.write(rendered)
    console_logger.warning(msg.decode())
    console_logger.warning('\n')
    console_logger.warning('-'*80)
    console_logger.warning(
        " * Don't forget to include package in app (import it in backend.py)")
    console_logger.warning(" * Don't forget to migrate DB & upgrade DB.")
    console_logger.warning(" * Don't forget to write package test.")
    console_logger.warning('-'*80)
    console_logger.warning('\n')


@MigrateCommand.command
def create(demo=False, superuser=False):
    """Creates a new Database and initialize with necessary data."""

    from flask_migrate import upgrade

    console_logger.debug("Upgrading...")
    upgrade()

    # I don't know why but alembic adds a Handler and disables mine, so after
    # `upgrade()` function is executed my `console_logger` doesn't log anymore.
    # To fix this I have to remove the StreamHandler added by Alembic and
    # re-enable my `console_logger`.
    console_logger.parent.removeHandler(console_logger.parent.handlers[0])
    console_logger.disabled = False

    populate()
    if superuser:
        createsuperuser(default=True)
    if demo:
        demo_data()


@MigrateCommand.command
def populate():
    """Populates your existing Database with initial data."""
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.exc import ProgrammingError
    from app.auth import init_auth
    from app.event_logs import init_event_logs

    try:
        console_logger.debug("Populating DB...")
        init_auth()
        init_event_logs()
    except IntegrityError as error:
        console_logger.critical(error)
    except ProgrammingError as error:
        console_logger.critical(error)


@MigrateCommand.command
def demo_data():
    """Populates DB with fake data for demo."""
    from app.auth import init_demo_auth
    from app.event_logs import init_demo_event_logs

    console_logger.warning("Loading DB with Sample Data...")
    init_demo_auth()
    init_demo_event_logs()


@MigrateCommand.command
def drop(force=False):
    """Drop your existing Database."""

    from sqlalchemy.exc import ProgrammingError
    from flask_script import prompt_bool
    from app.extensions import db

    if force or prompt_bool("Are you sure you want to lose all your data"):
        console_logger.debug("Dropping DB...")
        db.drop_all()
        try:
            db.engine.execute('DROP TABLE "alembic_version";')
        except ProgrammingError as error:
            console_logger.critical(error)


@MigrateCommand.command
def rebuild(demo=False, superuser=False):
    """Drop & Recreates Database."""
    drop(force=True)
    create(demo=demo, superuser=superuser)


@MigrateCommand.command
def backup(out="database.sql", force=False):
    """ Uses `pg_dump` in the docker container and gets SQL file for backup. """
    from subprocess import Popen

    # TODO: error handling

    filename = os.path.join(app.config.get('BACKUP_FOLDER'), out)

    if os.path.isfile(filename) and not force:
        cont = input('\033[1;31m{} already exists. Overwrite? [y/N] \033['
                     '0m'.format(filename))
        if cont.upper() != 'Y':
            console_logger.error('Exiting')
            return

    docker_container = app.config.get('DOCKER_CONTAINER')
    user = app.config.get('DB_USER')
    host = app.config.get('DB_HOST')
    port = app.config.get('DB_PORT')
    database = app.config.get('DB_NAME')
    backup_folder = app.config.get('BACKUP_FOLDER')
    bkp_cmd = "docker exec {} pg_dump -U {} -h {} -p {} -d {} > {}".format(
        docker_container,
        user,
        host,
        port,
        database,
        filename
    )

    Popen(bkp_cmd, shell=True)
    console_logger.debug("DB Backup saved in %s/%s", backup_folder, out)


@MigrateCommand.command
def restore(input_file="database.sql", permanent=True, verbose=False):
    """ Uses `psql` in the docker container and loads SQL file from backup. """
    from subprocess import Popen, STDOUT, PIPE
    from datetime import datetime

    # TODO: error handling

    filename = os.path.join(app.config.get('BACKUP_FOLDER'), input_file)

    if permanent:
        console_logger.info('No permanent mode detected')
        datetime_fmt = "%Y%m%d%H%M%S%f"
        bkp_file = os.path.join(app.config.get('BACKUP_FOLDER'),
                                'bkp_restore_{}.sql'.format(
                                 datetime.now().strftime(datetime_fmt))
                                )

        backup(out=bkp_file, force=True)

    drop(force=True)

    user = app.config.get('DB_USER')
    host = app.config.get('DB_HOST')
    port = app.config.get('DB_PORT')
    database = app.config.get('DB_NAME')
    restore_cmd = "psql -U {} -h {} -p {} -d {} < {}".format(
        user,
        host,
        port,
        database,
        filename
    )

    proc = Popen(restore_cmd, shell=True, stdout=PIPE, stderr=STDOUT)
    if verbose:
        stdout_value, stderr_value = proc.communicate()
        console_logger.debug('\nOUTPUT: ')
        console_logger.info(stdout_value.decode())
        if stderr_value:
            console_logger.warning('\nERROR: ')
            console_logger.warning(stderr_value.decode())

    console_logger.debug("DB Backup loaded from %s", filename)


if __name__ == '__main__':
    manager.run()
