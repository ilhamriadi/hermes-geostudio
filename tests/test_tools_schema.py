"""Tests for MCP tool schemas."""
from hermes_geostudio.tools import TOOL_NAMES, get_tool_names

def test_tool_count():
    expected = ["gee_check_connection", "gee_authenticate", "gee_search_imagery",
                "gee_create_composite", "gee_calculate_index", "gee_terrain_analysis",
                "gis_export_data", "map_create_layout", "report_create_pdf",
                "geostudio_run_workflow"]
    assert len(TOOL_NAMES) == len(expected), f"Expected {len(expected)} tools, got {len(TOOL_NAMES)}"
    for exp in expected:
        assert exp in TOOL_NAMES, f"Missing tool: {exp}"

def test_get_tool_names():
    names = get_tool_names()
    assert len(names) >= 5, f"Expected at least 5 tools, got {len(names)}"
