"""MCP Tool definitions for Hermes GeoStudio."""
from typing import Any
import os

try:
    from mcp.server.fastmcp import FastMCP
    _mcp_version = 1
except ImportError:
    try:
        from mcp.server.mcp import MCP
        FastMCP = MCP
        _mcp_version = 2
    except ImportError:
        FastMCP = None
        _mcp_version = 0

from .config import get_config
from .workflows.pipeline import run_workflow
from .gee.client import check_connection, is_initialized, authenticate_gee, initialize_gee


def _tool(fn):
    """Apply @mcp.tool() if available."""
    if FastMCP is not None:
        return FastMCP.tool()(fn)
    return fn


_mcp = FastMCP("hermes-geostudio") if FastMCP else None


@_tool
def gee_check_connection() -> dict[str, Any]:
    """Check connection status to Google Earth Engine."""
    return check_connection()


@_tool
def gee_authenticate() -> dict[str, Any]:
    """Start GEE OAuth authentication (opens browser for authorization)."""
    return authenticate_gee()


@_tool
def gee_search_imagery(
    area: dict[str, Any],
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31",
    satellite: str = "sentinel-2",
    max_cloud_cover: float = 20.0,
    max_results: int = 10,
) -> dict[str, Any]:
    """Search for satellite imagery over a study area and date range."""
    try:
        from .gee.imagery import search_imagery
        return search_imagery(area, start_date, end_date, satellite, max_cloud_cover, max_results)
    except ImportError as e:
        return {"success": False, "error": f"imagery module unavailable: {e}"}


@_tool
def gee_create_composite(
    area: dict[str, Any],
    start_date: str,
    end_date: str,
    satellite: str = "sentinel-2",
    composite_type: str = "median",
    visualization: str = "natural_color",
    scale: int = 10,
) -> dict[str, Any]:
    """Create a composite image from satellite imagery collection."""
    try:
        from .gee.imagery import create_composite
        return create_composite(area, start_date, end_date, satellite, composite_type, visualization, scale)
    except ImportError as e:
        return {"success": False, "error": f"imagery module unavailable: {e}"}


@_tool
def gee_calculate_index(
    area: dict[str, Any],
    index: str = "NDVI",
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31",
    satellite: str = "sentinel-2",
    scale: int = 10,
) -> dict[str, Any]:
    """Calculate spectral indices (NDVI, EVI, NDWI, MNDWI, NDBI, NDMI)."""
    try:
        from .gee.indices import calculate_index
        return calculate_index(area, index, start_date, end_date, satellite, scale)
    except ImportError as e:
        return {"success": False, "error": f"indices module unavailable: {e}"}


@_tool
def gee_terrain_analysis(
    area: dict[str, Any],
    dem_source: str = "SRTM",
    scale: int = 30,
) -> dict[str, Any]:
    """Analyze terrain (slope, aspect, elevation) from DEM data via GEE."""
    try:
        from .gee.terrain import terrain_analysis
        return terrain_analysis(area, dem_source, scale)
    except ImportError as e:
        return {"success": False, "error": f"terrain module unavailable: {e}"}


@_tool
def gis_export_data(
    input_path: str,
    format: str = "shp",
    output_dir: str = None,
    zip_shp: bool = True,
) -> dict[str, Any]:
    """Export GIS vector data to SHP, GeoJSON, or CSV format."""
    try:
        import geopandas as gpd
        from .gis.exporters import export_shp, export_geojson, export_csv
        output_dir = output_dir or get_config().output_dir
        os.makedirs(output_dir, exist_ok=True)
        gdf = gpd.read_file(input_path)
        base = os.path.join(output_dir, f"export_{format}")
        if format == "shp":
            return export_shp(gdf, base + ".shp", zip_output=(base + ".zip" if zip_shp else None))
        elif format == "geojson":
            return export_geojson(gdf, base + ".geojson")
        elif format == "csv":
            return export_csv(gdf, base + ".csv")
        return {"success": False, "error": f"Unknown format: {format}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@_tool
def map_create_layout(
    map_data_path: str,
    size: str = "A4_landscape",
    title: str = "Peta Analisis",
    source: str = "",
    date: str = "",
    crs: str = "EPSG:4326",
    dpi: int = 300,
) -> dict[str, Any]:
    """Create a professional map layout in PNG format (A4/A3 portrait/landscape)."""
    try:
        from .cartography.layout import create_map_layout
        out_path = os.path.join(get_config().output_dir, 
                                f"{title.lower().replace(chr(32), "_")}{"_"+date if date else ""}.png")
        return create_map_layout(map_data_path, out_path, size, title, source=source, date=date, crs=crs, dpi=dpi)
    except Exception as e:
        return {"success": False, "error": str(e)}


@_tool
def report_create_pdf(
    title: str,
    study_area: str,
    objective: str = "",
    data_sources: list[str] = None,
    methods: list[str] = None,
    results_text: str = "",
    map_images: list[str] = None,
    output_filename: str = "report.pdf",
) -> dict[str, Any]:
    """Create a professional PDF report with maps, tables, and methodology sections."""
    try:
        from .reporting.report import create_report_pdf
        output_path = os.path.join(get_config().output_dir, output_filename)
        return create_report_pdf(title, output_path, study_area, objective,
                                 data_sources or [], methods or [], results_text,
                                 map_images or [], author="NEXORA AI Team")
    except Exception as e:
        return {"success": False, "error": str(e)}


@_tool
def geostudio_run_workflow(
    task_type: str,
    study_area: dict[str, Any],
    params: dict[str, Any] = None,
    output_dir: str = None,
) -> dict[str, Any]:
    """Run a complete geospatial analysis workflow (slope, ndvi, composite, map, report)."""
    return run_workflow(task_type, study_area, params, output_dir)


TOOL_NAMES = [
    "gee_check_connection", "gee_authenticate", "gee_search_imagery",
    "gee_create_composite", "gee_calculate_index", "gee_terrain_analysis",
    "gis_export_data", "map_create_layout", "report_create_pdf",
    "geostudio_run_workflow",
]


def get_tool_names() -> list[str]:
    """Return list of registered tool names."""
    return TOOL_NAMES


def register_tools():
    """Register tools for Hermes Agent plugin mode."""
    return TOOL_NAMES


def get_mcp_server():
    """Get the MCP server instance (for stdio transport)."""
    return _mcp
