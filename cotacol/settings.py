from environs import Env


env = Env()
env.read_env()

ENV = env.str("FLASK_ENV", default="production")
DEBUG = ENV == "development"
SECRET_KEY = env.str("FLASK_SECRET_KEY")
CACHE_REDIS_URL = env.str("REDIS_URL", default=None)
CACHE_TYPE = env.str("FLASK_CACHE_TYPE", default="null" if not CACHE_REDIS_URL else "redis")
CACHE_DEFAULT_TIMEOUT = 60 * 60 * 24  # 24 hours
