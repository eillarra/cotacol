import polyline  # type: ignore

from flask import url_for
from geojson import Feature, LineString  # type: ignore
from geojson.utils import coords  # type: ignore
from typing import List, NamedTuple, NewType, Optional, Tuple


LngLat = NewType("LngLat", Tuple[float, float])


class Climb(NamedTuple):
    id: int
    name: str
    coordinates: List[LngLat] = []
    city: Optional[str] = None
    province: Optional[str] = None
    cotacol_points: Optional[int] = None
    distance: Optional[int] = None
    elev_difference: Optional[int] = None
    avg_grade: Optional[float] = None

    @property
    def polyline(self) -> Optional[str]:
        return polyline.encode(self.coordinates, geojson=True) if len(self.coordinates) else None

    def asdict(self, *, include_coordinates: bool = True, include_api_url: bool = True) -> dict:
        d = self._asdict()

        if not include_coordinates:
            d.pop("coordinates")

        return {
            **d,
            **{
                "polyline": self.polyline,
                "url": url_for("api.climb_detail", climb_id=self.id, _external=True) if include_api_url else None,
            },
        }

    @classmethod
    def from_feature(cls, feature: Feature) -> "Climb":
        return cls(
            **{
                **{"id": feature.id, "coordinates": list(coords(feature)) if feature.geometry else []},
                **feature.properties,
            }
        )

    def to_feature(self) -> Feature:
        geometry = LineString(self.coordinates) if len(self.coordinates) > 0 else []
        properties = self.asdict(include_coordinates=False, include_api_url=False)
        properties.pop("id")
        properties.pop("polyline")
        properties.pop("url")
        return Feature(id=self.id, geometry=geometry, properties=properties)
