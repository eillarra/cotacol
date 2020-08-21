import click

from flask.cli import with_appcontext

from cotacol.extensions import cache
from .services.parser import update_cotacol_data


@click.command("clear_cache")
def clear_cache():
    """Empties application’s cache."""
    cache.clear()


@click.command("update_data")
@with_appcontext
def update_data():
    """Creates a basic GeoJson object with all information from Google Maps: https://tinyurl.com/rnrwszj."""
    update_cotacol_data()
