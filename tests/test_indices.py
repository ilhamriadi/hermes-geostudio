"""Tests for spectral index calculations."""
import pytest
from hermes_geostudio.gee.indices import INDEX_DEFINITIONS, _resolve_band_name

def test_index_definitions():
    assert "NDVI" in INDEX_DEFINITIONS
    assert INDEX_DEFINITIONS["NDVI"]["bands"] == ["NIR", "RED"]
    assert INDEX_DEFINITIONS["EVI"]["formula"] == "2.5 * ((NIR - RED) / (NIR + 6*RED - 7.5*BLUE + 1))"

def test_resolve_band_name_sentinel():
    assert _resolve_band_name("NIR", "sentinel-2") == "B8"
    assert _resolve_band_name("RED", "sentinel-2") == "B4"
    assert _resolve_band_name("SWIR1", "sentinel-2") == "B11"

def test_resolve_band_name_landsat():
    assert _resolve_band_name("NIR", "landsat-8") == "NIR"
    assert _resolve_band_name("RED", "landsat-8") == "Red"
