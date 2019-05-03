from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from config import app_config

import os
import sys

# Initialize SQL-Alchemy
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    import logging
    logging.basicConfig(
        level=logging.getLevelName(app.config.get("LOG_LEVEL")),
        format=os.getenv('LOGGING_FORMAT')
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting app")
    db.init_app(app)

    return app
