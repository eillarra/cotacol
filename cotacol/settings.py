from environs import Env


env = Env()
env.read_env()

ENV = env.str("FLASK_ENV", default="production")
DEBUG = ENV == "development"
SECRET_KEY = env.str("FLASK_SECRET_KEY")
COMPRESS_MIMETYPES = [
    "text/html",
    "text/css",
    "text/xml",
    "application/javascript",
    "application/json",
    "application/geo+json",
]
