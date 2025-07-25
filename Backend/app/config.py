import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:19200260@localhost:5432/ResidentHub")
    SQLALCHEMY_TRACK_MODIFICATIONS = False