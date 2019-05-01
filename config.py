import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').format(
        user=os.getenv('DATABASE_USER'),
        pw=os.getenv('DATABASE_PASS'),
        host=os.getenv('DATABASE_HOST'),
        db=os.getenv('DATABASE_NAME')
    )


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL').format(
        user=os.getenv('TEST_DATABASE_USER'),
        pw=os.getenv('TEST_DATABASE_PASS'),
        host=os.getenv('TEST_DATABASE_HOST'),
        db=os.getenv('TEST_DATABASE_NAME')
    )


app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
