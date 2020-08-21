from authlib.integrations.flask_client import OAuth  # type: ignore
from flask_assets import Environment  # type: ignore
from flask_caching import Cache  # type: ignore
from flask_login import LoginManager  # type: ignore
from flask_migrate import Migrate  # type: ignore
from flask_sqlalchemy import SQLAlchemy  # type: ignore


assets = Environment()
cache = Cache()
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
oauth = OAuth()
