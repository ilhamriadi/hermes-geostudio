"""Tests for map layout creation."""
import pytest
import os
from hermes_geostudio.cartography.layout import LAYOUT_SIZES, create_map_layout

def test_layout_sizes():
    assert LAYOUT_SIZES["A4_portrait"] == (210, 297)
    assert LAYOUT_SIZES["A4_landscape"] == (297, 210)
    assert LAYOUT_SIZES["A3_portrait"] == (297, 420)
    assert LAYOUT_SIZES["A3_landscape"] == (420, 297)

def test_create_layout_empty(tmp_path):
    result = create_map_layout(
        map_data_path="/nonexistent.tif",
        output_path=str(tmp_path / "test.png"),
        title="Test Map",
    )
    # Should fail gracefully since input doesn't exist
    assert "error" in result or not result.get("success", True)
