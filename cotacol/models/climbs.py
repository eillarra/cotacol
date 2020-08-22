import polyline  # type: ignore

from flask import url_for
from geojson import Feature, LineString  # type: ignore
from typing import List, Optional, Tuple

from cotacol.extensions import db


class Climb(db.Model):
    id = db.Column(db.SmallInteger, primary_key=True)
    name = db.Column(db.String(160))
    city = db.Column(db.String(160))
    province = db.Column(db.String(160))
    cotacol_points = db.Column(db.SmallInteger)
    distance = db.Column(db.SmallInteger)
    elevation_diff = db.Column(db.SmallInteger)
    avg_grade = db.Column(db.Float(precision=3))
    gpx_points = db.Column(db.JSON)
    extra_data = db.Column(db.JSON)

    @property
    def coordinates(self) -> Optional[List[Tuple[float, float, float]]]:
        if not self.gpx_points or not len(self.gpx_points):
            return None

        return [(c["lat"], c["lon"], c["ele"]) for c in self.gpx_points]

    @property
    def polyline(self) -> Optional[str]:
        return polyline.encode(self.coordinates) if self.coordinates else None

    @property
    def url(self) -> str:
        return url_for("api.climb_detail", climb_id=self.id, _external=True)

    def as_dict(self, *, exclude_coordinates: bool = False) -> dict:
        d = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        d["polyline"] = self.polyline
        d["url"] = self.url

        if not exclude_coordinates:
            d["coordinates"] = self.coordinates

        d.pop("gpx_points")

        return d

    def as_feature(self) -> Feature:
        geometry = []

        if self.gpx_points and len(self.gpx_points):
            geometry = LineString([(c["lon"], c["lat"], c["ele"]) for c in self.gpx_points])

        properties = self.as_dict(exclude_coordinates=True)
        properties.pop("id")
        properties.pop("polyline")
        properties.pop("url")
        return Feature(id=self.id, geometry=geometry, properties=properties)
