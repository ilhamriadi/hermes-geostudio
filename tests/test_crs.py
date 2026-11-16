"""Tests for CRS utilities."""
from hermes_geostudio.gis.crs import validate_crs, auto_crs_for_area

def test_validate_crs_valid():
    result = validate_crs("EPSG:4326")
    assert result["valid"] is True
    assert result["crs"] == "EPSG:4326"

def test_validate_crs_invalid():
    result = validate_crs("INVALID:9999")
    assert result["valid"] is False

def test_auto_crs_for_indonesia():
    crs = auto_crs_for_area(107.5, -7.3, 107.9, -6.9)
    assert crs in ["EPSG:32633", "EPSG:32733", "EPSG:4326"]
