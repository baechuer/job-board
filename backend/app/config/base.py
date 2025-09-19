import os

class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    # Token lifetimes
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "900"))  # seconds
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "1209600"))  # 14 days
    JSON_SORT_KEYS = False
