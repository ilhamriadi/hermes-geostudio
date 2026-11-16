"""CRS validation and conversion utilities."""
from typing import Optional
from pyproj import CRS, Transformer

VALID_CRS = {
    "EPSG:4326": "WGS 84",
    "EPSG:32632": "UTM zone 32N",
    "EPSG:32633": "UTM zone 33N",
    "EPSG:32634": "UTM zone 34N",
    "EPSG:32732": "UTM zone 32S",
    "EPSG:32733": "UTM zone 33S",
    "EPSG:32734": "UTM zone 34S",
}

def validate_crs(crs: str) -> dict:
    try:
        c = CRS(crs)
        return {"valid": True, "crs": crs, "name": c.name, "units": str(c.axis_info[0].unit_name) if c.axis_info else "unknown"}
    except Exception as e:
        return {"valid": False, "crs": crs, "error": str(e)}

def auto_crs_for_area(lon_min: float, lat_min: float, lon_max: float, lat_max: float) -> str:
    center_lon = (lon_min + lon_max) / 2
    if 0 <= center_lon < 6: return "EPSG:32632"
    elif 6 <= center_lon < 12: return "EPSG:32633"
    elif 12 <= center_lon < 18: return "EPSG:32634"
    elif -6 <= center_lon < 0: return "EPSG:32732"
    elif -12 <= center_lon < -6: return "EPSG:32733"
    elif -18 <= center_lon < -12: return "EPSG:32734"
    return "EPSG:4326"

def get_utM_crs(lon: float) -> str:
    zone = int((lon + 180) / 6) + 1
    epsg_north = 32600 + zone
    epsg_south = 32700 + zone
    return epsg_north if 0 <= lon < 180 else epsg_south
