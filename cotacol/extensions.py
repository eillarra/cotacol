from authlib.integrations.flask_client import OAuth  # type: ignore
from flask_assets import Environment  # type: ignore
from flask_caching import Cache  # type: ignore


assets = Environment()
cache = Cache()
oauth = OAuth()
