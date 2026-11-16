"""End-to-end workflow orchestrator for GeoStudio."""
from typing import Any, Literal
from datetime import datetime
import os
from ..config import get_config
from ..gee.client import check_connection, is_initialized, initialize_gee
from ..gee.imagery import search_imagery, create_composite
from ..gee.indices import calculate_index
from ..gee.terrain import terrain_analysis
from ..cartography.layout import create_map_layout
from ..reporting.report import create_report_pdf

TASK_TYPES = {
    "slope": "terrain",
    "ndvi": "index",
    "landcover": "classification",
    "composite": "imagery",
    "map": "cartography",
    "report": "reporting",
}

def run_workflow(
    task_type: Literal["slope", "ndvi", "landcover", "composite", "map", "report"],
    study_area: dict[str, Any],
    params: dict[str, Any] = None,
    output_dir: str = None,
) -> dict[str, Any]:
    """High-level workflow runner.

    Args:
        task_type: Type of analysis to run
        study_area: Area specification (WKT, bbox, GeoJSON)
        params: Task-specific parameters
        output_dir: Output directory override

    Returns:
        Dict with results, output paths, and status.
    """
    params = params or {}
    config = get_config()
    out_dir = output_dir or config.output_dir
    os.makedirs(out_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    result = {"success": False, "task_type": task_type, "study_area": study_area,
               "output_dir": out_dir, "timestamp": ts}

    try:
        # Ensure GEE is connected
        if not is_initialized():
            conn = check_connection()
            if not conn.get("success"):
                return {**result, "error": "GEE not initialized. Run auth first."}

        if task_type == "slope":
            terrain_result = terrain_analysis(
                area=study_area,
                dem_source=params.get("dem_source", "SRTM"),
                scale=params.get("scale", 30),
            )
            if terrain_result["success"]:
                slope_path = os.path.join(out_dir, f"slope_{ts}.tif")
                terrain_result["output_path"] = slope_path
            result.update(terrain_result)

        elif task_type == "ndvi":
            idx_result = calculate_index(
                area=study_area,
                index="NDVI",
                start_date=params.get("start_date", "2024-01-01"),
                end_date=params.get("end_date", "2024-12-31"),
                satellite=params.get("satellite", "sentinel-2"),
                scale=params.get("scale", 10),
            )
            result.update(idx_result)

        elif task_type == "composite":
            comp_result = create_composite(
                area=study_area,
                start_date=params.get("start_date", "2024-01-01"),
                end_date=params.get("end_date", "2024-12-31"),
                satellite=params.get("satellite", "sentinel-2"),
                composite_type=params.get("composite_type", "median"),
                visualization=params.get("visualization", "natural_color"),
                scale=params.get("scale", 10),
            )
            result.update(comp_result)

        elif task_type == "map":
            map_input = params.get("map_input", [])
            if isinstance(map_input, str):
                map_input = [map_input]
            layout_result = create_map_layout(
                map_data_path=map_input[0] if map_input else "",
                output_path=os.path.join(out_dir, f"map_{ts}.png"),
                size=params.get("size", "A4_landscape"),
                title=params.get("title", "Peta Analisis"),
                legend_items=params.get("legend_items"),
                source=params.get("source", ""),
                date=params.get("date", datetime.now().strftime("%Y")),
                crs=params.get("crs", "EPSG:4326"),
            )
            result.update(layout_result)

        elif task_type == "report":
            report_params = {
                "title": params.get("title", "Laporan Analisis Geospasial"),
                "study_area": str(study_area),
                "objective": params.get("objective", ""),
                "data_sources": params.get("data_sources", []),
                "methods": params.get("methods", []),
                "results_text": params.get("results_text", ""),
                "map_images": params.get("map_images", []),
                "tables": params.get("tables", []),
                "author": params.get("author", "NEXORA AI Team"),
            }
            pdf_path = os.path.join(out_dir, f"report_{ts}.pdf")
            report_result = create_report_pdf(pdf_path, **report_params)
            result.update(report_result)

        result["success"] = True
        result["message"] = f"Workflow '{task_type}' completed successfully."

    except Exception as e:
        result["error"] = str(e)
        result["message"] = f"Workflow failed: {e}"

    return result
