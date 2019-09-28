"""fwe, flask webauthn example"""

import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import generate_csrf


db = SQLAlchemy()  # pylint: disable=invalid-name
login_manager = LoginManager()  # pylint: disable=invalid-name


def create_app(dbconnection='postgresql:///fwe'):
    """application factory"""

    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or os.urandom(32)
    app.config['SQLALCHEMY_DATABASE_URI'] = dbconnection
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'app.login_route'
    login_manager.login_message = 'Not logged in'
    login_manager.login_message_category = 'warning'

    from fwe import controller  # pylint: disable=cyclic-import
    app.register_blueprint(controller.blueprint, url_prefix='/')
    from fwe import commands  # pylint: disable=cyclic-import
    app.cli.add_command(commands.dbinit_command)
    app.cli.add_command(commands.dbremove_command)

    # least intrusive way to pass token into every view without enforcing csrf on all routes
    app.add_template_global(name='csrf_token', f=generate_csrf)

    return app
