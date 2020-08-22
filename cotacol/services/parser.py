import csv
import json
import os
import re
import requests

from geojson import FeatureCollection, load as load_geojson  # type: ignore
from typing import List

from cotacol.extensions import db
from cotacol.models import Climb


LOCATION = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
GPX_PATH = (
    "https://raw.githubusercontent.com/CotacolHunting/COTACOL-iOS/master/COTACOL/Data/data.gpx"
    "?token=AAD5UHK7M7QBI7KWOFYVEEC7IDSIW"
)


def update_cotacol_data() -> None:
    """
    """
    climbs = {}

    # Generate initial list of cols from generic list

    with open(os.path.join(LOCATION, "../data", "cotacol.csv")) as f:
        csv_reader = csv.reader(f, delimiter=",")
        next(csv_reader)
        for row in csv_reader:
            climb_id = int(row[0])
            climbs[climb_id] = Climb(
                id=climb_id,
                name=row[3],
                city=row[2],
                province=row[1],
                cotacol_points=int(row[9]),
                distance=int(row[8]),
                elevation_diff=int(row[7]),
                avg_grade=float(row[4]),
            )

    # Add extra info from GPX

    try:
        from gpxpy import parse as parse_gpx  # type: ignore
        source = requests.get(GPX_PATH).text.encode("utf-8")
        gpx = parse_gpx(source)
    except Exception as e:
        raise ValueError(e)

    for track in gpx.tracks:
        gpx_points: List[dict] = []

        for segment in track.segments:
            for point in segment.points:
                gpx_points.append({"lat": point.latitude, "lon": point.longitude, "ele": point.elevation})

        cotacol_id = int(re.findall(r"\d+", track.name)[0])
        climbs[cotacol_id].gpx_points = gpx_points

    # Generate GeoJSON file

    with open(os.path.join(LOCATION, "../data", "cotacol.geojson"), "w") as file:
        geojson = FeatureCollection([climb.as_feature() for climb in list(climbs.values())])
        file.write(json.dumps(geojson))

    return


def sync_db_climbs() -> None:
    """
    """
    with open(os.path.join(LOCATION, "../data", "cotacol.geojson")) as json_file:
        collection = load_geojson(json_file)

    for feature in collection.features:
        gpx_points = [{"lat": g[1], "lon": g[0], "ele": g[2]} for g in feature.geometry.coordinates]
        climb = Climb(id=feature.id, gpx_points=gpx_points, **feature.properties)
        db.session.merge(climb)

    db.session.flush()
    db.session.commit()

    return
