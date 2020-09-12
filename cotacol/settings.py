from environs import Env


env = Env()
env.read_env()

ENV = env.str("FLASK_ENV", default="production")
DEBUG = ENV == "development"
SECRET_KEY = env.str("FLASK_SECRET_KEY")
SERVER_NAME = env.str("FLASK_SERVER_NAME")
COMPRESS_MIMETYPES = [
    "text/html",
    "text/css",
    "text/xml",
    "application/javascript",
    "application/json",
    "application/geo+json",
]

SQLALCHEMY_DATABASE_URI = env.str("DATABASE_URL")
SQLALCHEMY_TRACK_MODIFICATIONS = False

STRAVA_CLIENT_ID = env.int("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = env.str("STRAVA_CLIENT_SECRET")
STRAVA_ACCESS_TOKEN_URL = "https://www.strava.com/oauth/token"
STRAVA_API_BASE_URL = "https://www.strava.com/api/v3"
STRAVA_AUTHORIZE_URL = "https://www.strava.com/oauth/authorize"
STRAVA_CLIENT_KWARGS = {
    "response_type": "code",
    "scope": "read",
    "token_endpoint_auth_method": "client_secret_post",
}
