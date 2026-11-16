"""Vector processing utilities."""
import geopandas as gpd
from shapely.geometry import mapping
from typing import Any
from .crs import validate_crs, auto_crs_for_area

def calculate_area(gdf: gpd.GeoDataFrame, class_column: str) -> dict:
    gdf = gdf.to_crs("EPSG:4326")
    gdf_utm = gdf.to_crs(auto_crs_for_area(
        gdf.total_bounds[0], gdf.total_bounds[1],
        gdf.total_bounds[2], gdf.total_bounds[3]))
    gdf_utm["area_m2"] = gdf_utm.geometry.area
    stats = gdf_utm.groupby(class_column, dropna=False)["area_m2"].agg(["sum", "count"]).reset_index()
    stats.columns = [class_column, "area_m2", "count"]
    stats["area_ha"] = stats["area_m2"] / 10000
    return {
        "success": True, "total_area_m2": float(gdf_utm.area.sum()),
        "total_area_ha": float(gdf_utm.area.sum() / 10000),
        "classes": [{c: r[class_column], "area_m2": float(r["area_m2"]),
                     "area_ha": float(r["area_ha"]), "count": int(r["count"])}
                    for _, r in stats.iterrows()],
    }

def reproject_vector(input_path: str, output_path: str, target_crs: str = "EPSG:4326") -> dict:
    try:
        gdf = gpd.read_file(input_path)
        src_crs = str(gdf.crs)
        valid = validate_crs(target_crs)
        if not valid["valid"]:
            return {"success": False, "error": f"Invalid CRS: {target_crs}"}
        gdf = gdf.to_crs(target_crs)
        gdf.to_file(output_path)
        return {"success": True, "input": input_path, "output": output_path,
                "source_crs": src_crs, "target_crs": target_crs, "features": len(gdf)}
    except Exception as e:
        return {"success": False, "error": str(e)}
