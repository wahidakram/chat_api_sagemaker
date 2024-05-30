import os
from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'
    app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024
    CORS(app)
    from . import view
    app.register_blueprint(view.bp)
    return app
