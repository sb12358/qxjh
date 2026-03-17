import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "qxjh-dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:eiNg6pie@10.10.10.120:3306/qxjh_platform?charset=utf8mb4",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
