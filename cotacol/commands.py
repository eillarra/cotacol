import click

from .data.parser import parse_cotacol_data


@click.command("parse")
def parse_data():
    """Creates a basic GeoJson object with all information from Google Maps: https://tinyurl.com/rnrwszj."""
    parse_cotacol_data()
