# default config
class BaseConfig(object):
    """BasicConfig of the app"""
    DEBUG=False
    SECRET_KEY='development key'
    USERNAME='admin'
    PASSWORD='default'

class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:////tmp/test.db'

class DevelopmentConfig(BaseConfig):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(BaseConfig):
    DEBUG=False
