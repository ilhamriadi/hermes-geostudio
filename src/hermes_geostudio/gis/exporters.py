"""GIS data export utilities."""
import os
import zipfile
import geopandas as gpd
import rasterio
from typing import Any

def export_shp(gdf: gpd.GeoDataFrame, output_path: str, zip_output: str = None) -> dict:
    try:
        out_dir = os.path.dirname(output_path) or "."
        base = os.path.splitext(output_path)[0]
        gdf.to_file(base + ".shp")
        files_created = [base + ext for ext in [".shp", ".shx", ".dbf", ".prj", ".cpg"]]
        result = {"success": True, "files": files_created, "format": "Shapefile"}
        if zip_output:
            with zipfile.ZipFile(zip_output, "w", zipfile.ZIP_DEFLATED) as zf:
                for fp in files_created:
                    if os.path.exists(fp):
                        zf.write(fp, os.path.basename(fp))
                result["zip_path"] = zip_output
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

def export_geotiff(raster_path: str, output_path: str, crs: str = "EPSG:4326") -> dict:
    try:
        with rasterio.open(raster_path) as src:
            kwargs = src.meta.copy()
            kwargs.update({"crs": crs, "compress": "deflate"})
            with rasterio.open(output_path, "w", **kwargs) as dst:
                dst.write(src.read())
        return {"success": True, "output": output_path, "crs": crs, "size_mb": os.path.getsize(output_path) / 1e6}
    except Exception as e:
        return {"success": False, "error": str(e)}

def export_geojson(gdf: gpd.GeoDataFrame, output_path: str) -> dict:
    try:
        gdf.to_file(output_path, driver="GeoJSON")
        return {"success": True, "output": output_path, "features": len(gdf), "size_kb": os.path.getsize(output_path) / 1024}
    except Exception as e:
        return {"success": False, "error": str(e)}

def export_csv(gdf: gpd.GeoDataFrame, output_path: str, exclude_geom: bool = True) -> dict:
    try:
        df = gdf.drop(columns=["geometry"], errors="ignore") if exclude_geom else gdf
        df.to_csv(output_path, index=False)
        return {"success": True, "output": output_path, "rows": len(df), "columns": list(df.columns)}
    except Exception as e:
        return {"success": False, "error": str(e)}
