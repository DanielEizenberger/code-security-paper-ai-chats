import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')

    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://root:123"
        f"@127.0.0.1/footballclub"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
