import os

from geojson import FeatureCollection, load as load_geojson  # type: ignore
from typing import Dict

from cotacol.extensions import cache
from .models import Climb


@cache.cached()
def get_climbs() -> Dict[int, Climb]:
    collection = get_geojson()
    cols = {}

    for feature in collection.features:
        cols[feature.id] = Climb.from_feature(feature)

    return cols


@cache.cached()
def get_geojson() -> FeatureCollection:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    with open(os.path.join(__location__, "../data", "cotacol.geojson")) as json_file:
        collection = load_geojson(json_file)

    return collection
