from main_app.gcloud_functions import getCloudSqlUrl, getSqlEngineOptions
import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "12345678901234567890")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    cloudSqlUrl = getCloudSqlUrl()
    cloudSqlEngineOptions = getSqlEngineOptions()

    # SQLALCHEMY_DATABASE_URI = cloudSqlUrl
    # SQLALCHEMY_ENGINE_OPTIONS = cloudSqlEngineOptions

    # Set environment variables necessary for Google login and API usage
    USE_GOOGLE_LOGIN_AND_API = "True"
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "12345678901234567890")
    GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "12345678901234567890")
    WTF_CSRF_TIME_LIMIT = None
