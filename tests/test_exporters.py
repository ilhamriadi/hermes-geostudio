"""Tests for GIS exporters."""
import pytest
import geopandas as gpd
from shapely.geometry import Point
from hermes_geostudio.gis.exporters import export_geojson, export_csv

def test_export_geojson(tmp_path):
    gdf = gpd.GeoDataFrame({"name": ["A"], "value": [1]}, geometry=[Point(0, 0)], crs="EPSG:4326")
    out = tmp_path / "test.geojson"
    result = export_geojson(gdf, str(out))
    assert result["success"] is True
    assert out.exists()

def test_export_csv_no_geom(tmp_path):
    """Test CSV export without geometry column."""
    gdf = gpd.GeoDataFrame({"name": ["A", "B"], "value": [1, 2]})
    out = tmp_path / "test.csv"
    result = export_csv(gdf, str(out))
    assert result["success"] is True
    assert result["rows"] == 2

def test_export_shp_zip(tmp_path):
    from hermes_geostudio.gis.exporters import export_shp
    gdf = gpd.GeoDataFrame({"name": ["A"]}, geometry=[Point(0, 0)], crs="EPSG:4326")
    out = tmp_path / "test.shp"
    result = export_shp(gdf, str(out), zip_output=str(tmp_path / "test.zip"))
    assert result["success"] is True
