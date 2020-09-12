import os

from flask import Flask
from flask_compress import Compress  # type: ignore
from flask_cors import CORS  # type: ignore
from flask_talisman import Talisman  # type: ignore
from werkzeug.middleware.proxy_fix import ProxyFix

from .auth.views import auth
from .commands import clear_cache
from .extensions import assets, cache, oauth
from .site.views import site


def create_app(config_object="cotacol.settings") -> Flask:
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.
    :param config_object: The configuration object to use.
    """
    app = Flask(__name__, static_folder="_static")
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # type: ignore
    app.config.from_object(config_object)

    register_extensions(app)
    register_oauth_clients()
    register_blueprints(app)
    register_filters(app)
    register_commands(app)

    return app


def register_blueprints(app) -> None:
    """Register Flask blueprints."""
    app.register_blueprint(site)
    app.register_blueprint(auth, url_prefix="/u")


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(clear_cache)


def register_extensions(app):
    """Register Flask extensions."""
    Compress(app)
    CORS(app)
    Talisman(
        app,
        force_https=True,
        content_security_policy={
            "default-src": [
                "'self'",
                "'unsafe-eval'",
                "'unsafe-inline'",
                "blob:",
                "data:",
                "*.cloudfront.net",
                "*.mapbox.com",
                "fonts.googleapis.com",
                "fonts.gstatic.com",
                "api.cotacol.cc",
            ]
        },
    )

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
    oauth.init_app(app, cache=cache)


def register_filters(app):
    """Jinja filters."""
    app.jinja_env.globals["DEBUG"] = app.config["DEBUG"]


def register_oauth_clients():
    """Register OAuth client integrations."""
    oauth.register("strava")
