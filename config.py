import os
from dotenv import load_dotenv

load_dotenv()


class Config(object):
    SECRET_KEY = "aylacantik"
    SECURITY_PASSWORD_SALT = "aylacantik"
    SESSION_TYPE = "filesystem"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECURITY_TOKEN_AUTHENTICATION_HEADER = "Authentication-Token"
    TESTING = True
    LOGIN_DISABLED = True


class DevelopmentConfig(Config):

    DEBUG = True
