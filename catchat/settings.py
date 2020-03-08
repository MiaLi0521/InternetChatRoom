import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

if sys.platform.startswith('win'):
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class BaseConfig:
    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', prefix + os.path.join(basedir, 'data.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

    CATCHAT_MESSAGE_PER_PAGE = 10
    CATCHAT_ADMIN_EMAIL = os.getenv('CATCHAT_ADMIN_EMAIL', 'admin@helloflask.com')


class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


class TestConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'
    WTF_CSRF_ENABLE = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestConfig
}