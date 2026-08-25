"""
KML Parser for Farm Boundaries and Study Areas
"""
import xml.etree.ElementTree as ET
from typing import Dict, List, Tuple, Any
from shapely.geometry import Polygon, Point
import math


def parse_kml(kml_path: str) -> Dict[str, Any]:
    """
    Parses a KML file and extracts the polygon coordinates, bounding box, 
    Shapely geometry, centroid, and area.
    """
    tree = ET.parse(kml_path)
    root = tree.getroot()

    ns = {
        'kml': 'http://www.opengis.net/kml/2.2',
        'gx': 'http://www.google.com/kml/ext/2.2'
    }

    coord_elem = root.find('.//kml:coordinates', ns)
    if coord_elem is None:
        coord_elem = root.find('.//{http://www.opengis.net/kml/2.2}coordinates')
        if coord_elem is None:
            coord_elem = root.find('.//coordinates')

    if coord_elem is None or not coord_elem.text:
        raise ValueError(f"No coordinates found in KML file: {kml_path}")

    raw_text = coord_elem.text.strip()
    coord_tokens = raw_text.split()

    coords: List[Tuple[float, float]] = []
    for token in coord_tokens:
        parts = token.split(',')
        if len(parts) >= 2:
            lon = float(parts[0])
            lat = float(parts[1])
            coords.append((lon, lat))

    if len(coords) < 3:
        raise ValueError(f"At least 3 coordinate points required for polygon, found {len(coords)}")

    polygon = Polygon(coords)
    minx, miny, maxx, maxy = polygon.bounds
    centroid = polygon.centroid

    lat_mid = centroid.y
    km_per_deg_lat = 110.574
    km_per_deg_lon = 111.320 * math.cos(math.radians(lat_mid))
    
    area_sq_m = polygon.area * (km_per_deg_lat * 1000) * (km_per_deg_lon * 1000)
    area_hectares = area_sq_m / 10000.0
    area_acres = area_hectares * 2.47105

    name_elem = root.find('.//kml:Placemark/kml:name', ns)
    name = name_elem.text if name_elem is not None and name_elem.text else "Pilot Farm"

    return {
        "name": name,
        "kml_path": kml_path,
        "coordinates": coords,
        "polygon": polygon,
        "bounds": {
            "min_lon": minx,
            "min_lat": miny,
            "max_lon": maxx,
            "max_lat": maxy
        },
        "centroid": {
            "lon": centroid.x,
            "lat": centroid.y
        },
        "area": {
            "sq_meters": round(area_sq_m, 2),
            "hectares": round(area_hectares, 3),
            "acres": round(area_acres, 2)
        },
        "geojson": {
            "type": "Feature",
            "properties": {
                "name": name,
                "area_acres": round(area_acres, 2),
                "area_hectares": round(area_hectares, 3)
            },
            "geometry": {
                "type": "Polygon",
                "coordinates": [[list(pt) for pt in coords]]
            }
        }
    }


def get_study_catchment_bbox(farm_bounds: Dict[str, float], buffer_km: float = 5.0) -> Dict[str, float]:
    """
    Computes a broader catchment bounding box around the farm for hydrogeological analysis.
    """
    lat_mid = (farm_bounds["min_lat"] + farm_bounds["max_lat"]) / 2.0
    km_per_deg_lat = 110.574
    km_per_deg_lon = 111.320 * math.cos(math.radians(lat_mid))

    lat_buf = buffer_km / km_per_deg_lat
    lon_buf = buffer_km / km_per_deg_lon

    return {
        "min_lon": round(farm_bounds["min_lon"] - lon_buf, 5),
        "min_lat": round(farm_bounds["min_lat"] - lat_buf, 5),
        "max_lon": round(farm_bounds["max_lon"] + lon_buf, 5),
        "max_lat": round(farm_bounds["max_lat"] + lat_buf, 5),
        "buffer_km": buffer_km
    }


if __name__ == "__main__":
    import os
    kml_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Farm.kml"))
    if os.path.exists(kml_file):
        info = parse_kml(kml_file)
        print(f"Farm Name: {info['name']}")
        print(f"Centroid: {info['centroid']}")
        print(f"Area: {info['area']['acres']} Acres ({info['area']['hectares']} ha)")
        print(f"Bounds: {info['bounds']}")
        catchment = get_study_catchment_bbox(info['bounds'], buffer_km=6.0)
        print(f"Study Catchment BBox (6km buffer): {catchment}")
