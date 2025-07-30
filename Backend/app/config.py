import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:123456a@localhost:5444/ResiHub")
    SQLALCHEMY_TRACK_MODIFICATIONS = False