from flask import Flask
from flask_cors import CORS  # type: ignore
from flask_talisman import Talisman  # type: ignore
from werkzeug.middleware.proxy_fix import ProxyFix

from .api.views import api
from .commands import parse_data
from .extensions import cache
from .pwa.views import pwa


def create_app(config_object="cotacol.settings") -> Flask:
    """Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.
    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    app.config.from_object(config_object)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    return app


def register_blueprints(app) -> None:
    """Register Flask blueprints."""
    app.register_blueprint(api, url_prefix="/api")
    app.register_blueprint(pwa)


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(parse_data)


def register_extensions(app):
    """Register Flask extensions."""
    CORS(app)
    Talisman(
        app,
        force_https=True,
        content_security_policy={"default-src": ["'self'", "'unsafe-eval'", "'unsafe-inline'", "blob:"]},
    )
    cache.init_app(app)
