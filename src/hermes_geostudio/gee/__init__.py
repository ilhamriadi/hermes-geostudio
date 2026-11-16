"""Google Earth Engine module."""
from .client import initialize_gee, check_connection, is_initialized
try:
    from .imagery import search_imagery, create_composite
except ImportError:
    pass
try:
    from .indices import calculate_index
except ImportError:
    pass
try:
    from .terrain import terrain_analysis
except ImportError:
    pass

__all__ = ["initialize_gee", "check_connection", "is_initialized"]
