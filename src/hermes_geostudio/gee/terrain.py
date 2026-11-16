"""Terrain analysis using GEE DEM data."""
from typing import Any, Literal
import ee
from .client import is_initialized, initialize_gee

DEM_SOURCES = {
    "SRTM": "USGS/SRTM30_V003",
    "ASTER": "NASA/NASADEM_HGT/001",
    "Copernicus": "ESA/WorldCover/v100",
}

def _parse_area(area: Any):
    if isinstance(area, str):
        try:
            import json
            return ee.Geometry.WKT(area)
        except Exception:
            try:
                return ee.Geometry(_json.loads(area))
            except Exception:
                raise ValueError(f"Cannot parse area: {area[:100]}")
    if isinstance(area, dict):
        if "type" in area:
            return ee.Geometry.Polygon(area.get("coordinates", []))
        if all(k in area for k in ["minx", "miny", "maxx", "maxy"]):
            return ee.Geometry.BBox(area["minx"], area["miny"], area["maxx"], area["maxy"])
    if isinstance(area, (list, tuple)):
        if len(area) == 4 and all(isinstance(x, (int, float)) for x in area):
            return ee.Geometry.BBox(*area)
        return ee.Geometry.Polygon(area)
    raise ValueError(f"Unsupported area format: {type(area)}")

def terrain_analysis(
    area: Any,
    dem_source: Literal["SRTM", "ASTER"] = "SRTM",
    scale: int = 30,
) -> dict[str, Any]:
    """Analyze terrain (slope, aspect, elevation) from DEM data."""
    if not is_initialized():
        result = initialize_gee()
        if not result["success"]:
            return {"success": False, "error": result.get("message")}
    try:
        geometry = _parse_area(area)
        dem_id = DEM_SOURCES.get(dem_source, DEM_SOURCES["SRTM"])
        dem = ee.Image(dem_id)
        elevation = dem.select("elevation")
        slope = ee.Terrain.slope(elevation)
        aspect = ee.Terrain.aspect(elevation)

        # Export tasks
        task_name = f"geostudio_terrain_{dem_source.lower()}"
        elevation_task = ee.batch.Export.image.toDrive(
            image=elevation, description=f"{task_name}_elevation",
            folder="hermes_geostudio", region=geometry, scale=scale,
            maxPixels=1e13, crs="EPSG:4326", fileNamePrefix=f"{task_name}_elevation",
        )
        slope_task = ee.batch.Export.image.toDrive(
            image=slope, description=f"{task_name}_slope",
            folder="hermes_geostudio", region=geometry, scale=scale,
            maxPixels=1e13, crs="EPSG:4326", fileNamePrefix=f"{task_name}_slope",
        )
        elevation_task.start()
        slope_task.start()

        # Get stats
        elev_stats = elevation.reduceRegion(ee.Reducer.mean(), geometry, scale).getInfo()
        slope_stats = slope.reduceRegion(ee.Reducer.mean(), geometry, scale).getInfo()
        mean_elev = list(elev_stats.values())[0] if elev_stats else None
        mean_slope = list(slope_stats.values())[0] if slope_stats else None

        return {
            "success": True, "dem_source": dem_source, "scale_m": scale,
            "mean_elevation_m": round(float(mean_elev), 2) if mean_elev else None,
            "mean_slope_degrees": round(float(mean_slope), 2) if mean_slope else None,
            "tasks": [f"{task_name}_elevation", f"{task_name}_slope"],
            "output_format": "GeoTIFF (Google Drive)",
            "description": f"Slope and elevation exported. Mean elevation: {round(float(mean_elev), 2) if mean_elev else 'N/A'}m, Mean slope: {round(float(mean_slope), 2) if mean_slope else 'N/A'} deg",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
