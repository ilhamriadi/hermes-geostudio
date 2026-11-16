"""Raster processing utilities."""
import numpy as np
import rasterio
from rasterio.transform import from_bounds
from typing import Any
from .crs import validate_crs

def raster_stats(path: str, band: int = 1) -> dict:
    with rasterio.open(path) as src:
        data = src.read(band, masked=True)
        nodata = src.nodata
        return {
            "success": True, "path": path, "band": band,
            "min": float(data.min()), "max": float(data.max()),
            "mean": float(data.mean()), "std": float(data.std()),
            "count": int(np.count_nonzero(data)), "nodata_value": nodata,
            "crs": str(src.crs), "shape": list(data.shape),
        }

def clip_raster(input_path: str, output_path: str, bbox: tuple, crs: str = "EPSG:4326") -> dict:
    import rasterio
    from rasterio.mask import mask
    from rasterio.features import shape as feat_shape
    import numpy as np
    try:
        with rasterio.open(input_path) as src:
            # Simple bounding box crop via window
            bounds = src.bounds
            minx, miny, maxx, maxy = bbox
            # Find window
            col_off = max(0, int((minx - bounds.left) / src.res[0]))
            row_off = max(0, int((bounds.top - maxy) / abs(src.res[1])))
            width = min(src.width - col_off, max(1, int((maxx - minx) / src.res[0])))
            height = min(src.height - row_off, max(1, int((maxy - miny) / abs(src.res[1]))))
            with rasterio.open(
                output_path, "w", driver="GTiff", height=height, width=width,
                count=src.count, dtype=str(src.dtypes[0]), crs=crs,
                transform=rasterio.transform.from_bounds(minx, miny, maxx, maxy, width, height),
            ) as dst:
                dst.write(src.read(window=(slice(row_off, row_off+height), slice(col_off, col_off+width))))
            return {"success": True, "output": output_path, "bbox": bbox, "crs": crs}
    except Exception as e:
        return {"success": False, "error": str(e)}
