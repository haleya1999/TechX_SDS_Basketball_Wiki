from flaskr import pages
from flaskr.backend import User
from flask import Flask
from flask_login import LoginManager
import logging

logging.basicConfig(level=logging.DEBUG)

# The flask terminal command inside "run-flask.sh" searches for
# this method inside of __init__.py (containing flaskr module
# properties) as we set "FLASK_APP=flaskr" before running "flask".
class User:

    def __init__(self, username):
        self.username = username

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

def create_app(test_config=None):
    # Create and configure the app.
    app = Flask(__name__, instance_relative_config=True)
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User(user_id)

    # This is the default secret key used for login sessions
    # By default the dev environment uses the key 'dev'
    app.config.from_mapping(SECRET_KEY='dev',)

    if test_config is None:
        # Load the instance config, if it exists, when not testing.
        # This file is not committed. Place it in production deployments.
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in.
        app.config.from_mapping(test_config)

    # TODO(Project 1): Make additional modifications here for logging in, backends
    # and additional endpoints.
    pages.make_endpoints(app)
    return app
