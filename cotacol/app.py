import os

from flask import Flask
from flask_compress import Compress  # type: ignore
from flask_cors import CORS  # type: ignore
from werkzeug.middleware.proxy_fix import ProxyFix

from .commands import clear_cache
from .extensions import assets, cache
from .site.views import site


def create_app(config_object="cotacol.settings") -> Flask:
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.
    :param config_object: The configuration object to use.
    """
    app = Flask(__name__, static_folder="_static")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # type: ignore
    app.config.from_object(config_object)

    register_extensions(app)
    register_blueprints(app)
    register_filters(app)
    register_commands(app)

    return app


def register_blueprints(app) -> None:
    """Register Flask blueprints."""
    app.register_blueprint(site)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(clear_cache)


def register_extensions(app):
    """Register Flask extensions."""
    Compress(app)
    CORS(app)

    if "REDIS_URL" in os.environ:
        cache_config = {
            "CACHE_TYPE": "redis",
            "CACHE_REDIS_URL": os.environ.get("REDIS_URL"),
            "CACHE_DEFAULT_TIMEOUT": 60 * 60 * 6,  # 6 hours
        }
    else:
        cache_config = {"CACHE_TYPE": "null"}

    assets.init_app(app)
    cache.init_app(app, config=cache_config)


def register_filters(app):
    """Jinja filters."""
    app.jinja_env.globals["DEBUG"] = app.config["DEBUG"]
