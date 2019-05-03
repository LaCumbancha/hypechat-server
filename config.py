import os
basedir = os.path.abspath(os.path.dirname(__file__))

import logging

class Config(object):
    TESTING = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')


class ProductionConfig(Config):
    LOG_LEVEL = os.getenv('PROD_LOG_LEVEL')
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').format(
        user=os.getenv('PROD_DATABASE_USER'),
        pw=os.getenv('PROD_DATABASE_PASS'),
        host=os.getenv('PROD_DATABASE_HOST'),
        db=os.getenv('PROD_DATABASE_NAME')
    )


class DevelopmentConfig(Config):
    LOG_LEVEL = os.getenv('DEV_LOG_LEVEL')
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').format(
        user=os.getenv('DEV_DATABASE_USER'),
        pw=os.getenv('DEV_DATABASE_PASS'),
        host=os.getenv('DEV_DATABASE_HOST'),
        db=os.getenv('DEV_DATABASE_NAME')
    )


class TestingConfig(Config):
    LOG_LEVEL = os.getenv('BETA_LOG_LEVEL')
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').format(
        user=os.getenv('BETA_DATABASE_USER'),
        pw=os.getenv('BETA_DATABASE_PASS'),
        host=os.getenv('BETA_DATABASE_HOST'),
        db=os.getenv('BETA_DATABASE_NAME')
    )


app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
