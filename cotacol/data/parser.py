import csv
import json
import os
import re
import requests

from geojson import FeatureCollection  # type: ignore
from lxml import etree  # type: ignore
from typing import List, Set

from cotacol.api.models import Climb, LngLat


def parse_coordinates(coordinates: str) -> List[LngLat]:
    points = []

    for point in [p.strip() for p in coordinates.split("\n") if p.strip() != ""]:
        lng, lat, _ = [float(x) for x in point.split(",")]
        points.append(LngLat(tuple([lng, lat])))

    return points


def parse_cotacol_data() -> None:
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    climbs = {}

    # Generate initial list of cols from generic list

    with open(os.path.join(__location__, "cotacol.csv")) as f:
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
                elev_difference=int(row[7]),
                avg_grade=float(row[4]),
            )

    # Add extra info from Google Maps

    kml_path = "https://www.google.be/maps/d/u/0/kml?forcekml=1&mid=1AKYyZeVRsqoca1BC5cDDc_8aYF1OKvPW"

    try:
        source = requests.get(kml_path).text.encode("utf-8")
        tree = etree.fromstring(source, parser=etree.XMLParser(ns_clean=True))
    except Exception as e:
        raise ValueError(e)

    nsm = tree.nsmap
    nsm["kml"] = nsm.pop(None)
    map_ids: Set[int] = set()

    for el in tree.xpath("//kml:Placemark", namespaces=nsm):
        try:
            name = el.xpath(".//kml:name/text()", namespaces=nsm)[0]
            description = el.xpath(".//kml:description/text()", namespaces=nsm)[0].replace(",", ".")
            cotacol_id = int(re.findall(r"\d+", name)[0])

            if cotacol_id in map_ids or "Cotacol" not in description:
                continue

            map_ids.add(cotacol_id)

            d = climbs[cotacol_id]._asdict()
            d["coordinates"] = parse_coordinates(el.find(".//kml:coordinates", namespaces=nsm).text)
            climbs[cotacol_id] = Climb(**d)

        except IndexError:
            pass

    # Generate GeoJSON file that will be used by the app as reference

    with open(os.path.join(__location__, "cotacol.geojson"), "w") as file:
        geojson = FeatureCollection(
            [climb.to_feature() for climb in list(climbs.values())],
            properties={"title": "Encyclopedie COTACOL", "source": "Encyclopedie COTACOL"},
        )
        file.write(json.dumps(geojson, indent=2))

    return
