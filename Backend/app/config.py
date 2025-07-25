import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:Max14252@localhost:5432/ResiHub")
    SQLALCHEMY_TRACK_MODIFICATIONS = False