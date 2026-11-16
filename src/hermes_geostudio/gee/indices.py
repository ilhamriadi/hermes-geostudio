"""Spectral index calculations for GEE imagery."""
from typing import Literal, Any
import ee
from .client import is_initialized, initialize_gee

INDEX_DEFINITIONS: dict[str, dict[str, Any]] = {
    "NDVI": {"formula": "(NIR - RED) / (NIR + RED)", "bands": ["NIR", "RED"], "range": (-1, 1)},
    "EVI": {"formula": "2.5 * ((NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1))", "bands": ["NIR", "RED", "BLUE"], "range": (-1, 1)},
    "NDWI": {"formula": "(GREEN - NIR) / (GREEN + NIR)", "bands": ["GREEN", "NIR"], "range": (-1, 1)},
    "MNDWI": {"formula": "(GREEN - SWIR1) / (GREEN + SWIR1)", "bands": ["GREEN", "SWIR1"], "range": (-1, 1)},
    "NDBI": {"formula": "(SWIR1 - NIR) / (SWIR1 + NIR)", "bands": ["SWIR1", "NIR"], "range": (-1, 1)},
    "NDMI": {"formula": "(NIR - SWIR1) / (NIR + SWIR1)", "bands": ["NIR", "SWIR1"], "range": (-1, 1)},
}

S2_BAND_NAMES = {"NIR": "B8", "RED": "B4", "GREEN": "B3", "BLUE": "B2", "SWIR1": "B11", "SWIR2": "B12"}
LS_BAND_NAMES = {"NIR": "NIR", "RED": "Red", "GREEN": "Green", "BLUE": "Blue", "SWIR1": "SWIR1", "SWIR2": "SWIR2"}

def _resolve_band_name(band: str, satellite: str) -> str:
    band_map = S2_BAND_NAMES if satellite == "sentinel-2" else LS_BAND_NAMES
    return band_map.get(band, band)

def calculate_index(
    area: Any,
    index: Literal["NDVI", "EVI", "NDWI", "MNDWI", "NDBI", "NDMI"],
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31",
    satellite: str = "sentinel-2",
    scale: int = 10,
) -> dict[str, Any]:
    if not is_initialized():
        result = initialize_gee()
        if not result["success"]:
            return {"success": False, "error": result.get("message")}
    try:
        from .imagery import parse_area
        geometry = parse_area(area)
        collection_id = {"sentinel-2": "COPERNICUS/S2_SR_HARMONIZED",
                         "landsat-8": "LANDSAT/LC08/COL2/L1",
                         "landsat-9": "LANDSAT/LC09/COL2/L1"}.get(satellite, "COPERNICUS/S2_SR_HARMONIZED")
        col = (ee.ImageCollection(collection_id).filterDate(start_date, end_date)
               .filterBounds(geometry))
        img = col.median()
        idx_def = INDEX_DEFINITIONS[index]
        bands = [_resolve_band_name(b, satellite) for b in idx_def["bands"]]
        img = img.select(bands)
        b_vals = {b: img.bandNames().getInfo().index(n) for n, b in zip(bands, bands)}
        expr = idx_def["formula"]
        expr = expr.replace("NIR", bands[0]).replace("RED", bands[1] if len(bands) > 1 else "")
        if len(bands) > 2:
            expr = expr.replace("BLUE", bands[2])
            expr = expr.replace("SWIR1", bands[-1] if "SWIR" in expr else bands[1])
        idx_img = img.expression(expr)
        stats = idx_img.reduceRegion(ee.Reducer.mean(), geometry, scale).getInfo()
        mean_val = stats.get(list(stats.keys())[0], None) if stats else None
        return {
            "success": True, "index": index, "formula": idx_def["formula"],
            "satellite": satellite, "date_range": {"start": start_date, "end": end_date},
            "mean_value": round(float(mean_val), 4) if mean_val is not None else None,
            "band_names": bands, "scale_m": scale,
            "description": f"Mean {index} value over study area: {round(float(mean_val), 4) if mean_val else 'N/A'}",
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
