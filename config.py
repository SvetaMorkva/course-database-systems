import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://ka7610:123456@zanner.org.ua:33321/ka7610'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
