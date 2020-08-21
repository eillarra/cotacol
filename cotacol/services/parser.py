import csv
import json
import os
import re
import requests

from geojson import FeatureCollection  # type: ignore
from gpxpy import parse as parse_gpx  # type: ignore
from typing import List

from cotacol.extensions import db
from cotacol.models import Climb


def update_cotacol_data() -> None:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    climbs = {}

    # Generate initial list of cols from generic list

    with open(os.path.join(__location__, "../data", "cotacol.csv")) as f:
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

    # Add extra info from Google Maps

    gpx_path = "https://raw.githubusercontent.com/CotacolHunting/COTACOL-iOS/master/COTACOL/Data/data.gpx?token=AAD5UHME7BT7I72PA7WRVLC7IAXFW"

    try:
        source = requests.get(gpx_path).text.encode("utf-8")
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

    # Update database

    for climb in list(climbs.values()):
        db.session.merge(climb)

    db.session.flush()
    db.session.commit()

    # Generate GeoJSON file that can be downloaded in the app

    with open(os.path.join(__location__, "../data", "cotacol.geojson"), "w") as file:
        geojson = FeatureCollection(
            [climb.as_feature() for climb in Climb.query.all()],
            properties={"title": "COTACOL climbs", "source": "Encyclopedie COTACOL"},
        )
        file.write(json.dumps(geojson, indent=2))

    return
