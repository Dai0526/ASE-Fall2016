import os
# default config
class BaseConfig(object):
    """BasicConfig of the app"""
    #DATABASE=os.path.join(os.path.dirname(__file__), 'groupwise.db')
    DEBUG=False
    SECRET_KEY='development key'
    USERNAME='admin'
    PASSWORD='default'

class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class DevelopmentConfig(BaseConfig):
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///test.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class ProductionConfig(BaseConfig):
    DEBUG=False
