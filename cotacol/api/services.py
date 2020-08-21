import os

from geojson import FeatureCollection, load as load_geojson  # type: ignore

from cotacol.extensions import cache


@cache.cached(key_prefix="geojson")
def get_geojson() -> FeatureCollection:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

    with open(os.path.join(__location__, "../data", "cotacol.geojson")) as json_file:
        collection = load_geojson(json_file)

    return collection
