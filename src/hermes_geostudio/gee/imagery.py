"""Satellite imagery search and composite creation."""
from datetime import datetime
from typing import Any, Literal
import ee
import json

from .client import is_initialized, initialize_gee

SATELLITE_COLLECTIONS = {
    "sentinel-2": "COPERNICUS/S2_SR_HARMONIZED",
    "landsat-9": "LANDSAT/LC09/COL2/L1",
    "landsat-8": "LANDSAT/LC08/COL2/L1",
    "modis": "MODIS/061/MOD09AQ1",
}

VISUALIZATION_BANDS = {
    "natural_color": {"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000},
    "false_color": {"bands": ["B8", "B11", "B4"], "min": 0, "max": 10000},
    "ndvi_preview": {"bands": ["B8", "B4"], "min": 0, "max": 10000},
}


def parse_area(area):
    if isinstance(area, str):
        try:
            return ee.Geometry.WKT(area)
        except Exception:
            try:
                return ee.Geometry(json.loads(area))
            except Exception:
                raise ValueError(f"Cannot parse area: {area[:100]}")
    if isinstance(area, dict):
        if "type" in area:
            coords = area.get("coordinates", [])
            if area["type"] == "Polygon":
                return ee.Geometry.Polygon(coords)
            elif area["type"] == "Point":
                return ee.Geometry.Point(coords)
            return ee.Geometry.BBox(*coords[0]) if coords else ee.Geometry.BBox(0, 0, 1, 1)
        if all(k in area for k in ["minx", "miny", "maxx", "maxy"]):
            return ee.Geometry.BBox(area["minx"], area["miny"], area["maxx"], area["maxy"])
    if isinstance(area, (list, tuple)):
        if len(area) == 4 and all(isinstance(x, (int, float)) for x in area):
            return ee.Geometry.BBox(*area)
        return ee.Geometry.Polygon(area)
    raise ValueError(f"Unsupported area format: {type(area)}")


def search_imagery(area, start_date="2024-01-01", end_date="2024-12-31",
                   satellite="sentinel-2", max_cloud_cover=20.0, max_results=10):
    if not is_initialized():
        result = initialize_gee()
        if not result["success"]:
            return {"success": False, "error": result.get("message")}
    try:
        geometry = parse_area(area)
        collection_id = SATELLITE_COLLECTIONS.get(satellite, SATELLITE_COLLECTIONS["sentinel-2"])
        collection = (ee.ImageCollection(collection_id).filterDate(start_date, end_date)
                      .filterBounds(geometry).filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", max_cloud_cover)))
        count = collection.size().getInfo()
        first_img = collection.first()
        first_meta = first_img.toDictionary().getInfo() if first_img else {}
        date_arr = collection.aggregate_array("system:time_start").getInfo() or []
        from datetime import datetime as dt
        dates = [dt.fromtimestamp(d/1000).strftime("%Y-%m-%d") for d in date_arr[:5]]
        return {"success": True, "collection_id": collection_id, "satellite": satellite,
                "image_count": count, "date_range": {"start": start_date, "end": end_date},
                "sample_dates": dates, "bands_available": list(first_meta.keys())[:10] if first_meta else []}
    except Exception as e:
        return {"success": False, "error": str(e)}


def create_composite(area, start_date, end_date, satellite="sentinel-2",
                     composite_type="median", visualization="natural_color", scale=10):
    if not is_initialized():
        result = initialize_gee()
        if not result["success"]:
            return {"success": False, "error": result.get("message")}
    try:
        geometry = parse_area(area)
        collection_id = SATELLITE_COLLECTIONS.get(satellite, SATELLITE_COLLECTIONS["sentinel-2"])
        vis_config = VISUALIZATION_BANDS.get(visualization, VISUALIZATION_BANDS["natural_color"])
        collection = (ee.ImageCollection(collection_id).filterDate(start_date, end_date).filterBounds(geometry))
        comp_map = {"median": "median", "mean": "mean", "max": "max", "min": "min", "mosaic": "mosaic"}
        composite = getattr(collection, comp_map.get(composite_type, "median"))()
        composite = composite.select(vis_config["bands"])
        task_name = f"geostudio_composite_{datetime.now().strftime(chr(37)+"Y"+chr(37)+"m"+chr(37)+"d"+chr(37)+"H"+chr(37)+"M"+chr(37)+"S")}"
        ee.batch.Export.image.toDrive(image=composite, description=task_name, folder="hermes_geostudio",
                                      region=geometry, scale=scale, maxPixels=1e13, crs="EPSG:4326").start()
        preview_url = composite.getThumbURL({"dimensions": 800, "bands": vis_config["bands"],
                                              "min": vis_config.get("min", 0), "max": vis_config.get("max", 10000)})
        cloud_cover = collection.aggregate_mean("CLOUDY_PIXEL_PERCENTAGE").getInfo()
        return {"success": True, "task_id": task_name, "preview_url": preview_url,
                "composite_type": composite_type,
                "cloud_cover_avg": round(float(cloud_cover), 2) if cloud_cover else None,
                "scale_m": scale, "message": f"Composite exported to Drive as '{task_name}'"}
    except Exception as e:
        return {"success": False, "error": str(e)}
