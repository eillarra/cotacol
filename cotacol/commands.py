import click

from flask.cli import with_appcontext

from cotacol.extensions import cache
from .services.parser import update_cotacol_data, sync_db_climbs


@click.command("clear_cache")
def clear_cache():
    """Empties application’s cache."""
    cache.clear()


@click.command("update_data")
@with_appcontext
def update_data():
    """Creates a GeoJSON object with all COTACOL information."""
    update_cotacol_data()


@click.command("sync_db")
@with_appcontext
def sync_db():
    """Sync climbs list in database, from generic GeoJSON."""
    sync_db_climbs()
