import os

class Config:
    SECRET_KEY = 'super-secret-key'

    SQLALCHEMY_DATABASE_URI = (
        'mysql+pymysql://root:123@127.0.0.1/football_club'
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
