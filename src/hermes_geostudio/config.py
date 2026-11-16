"""Configuration management for Hermes GeoStudio."""

import os
import json
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field


class GEEConfig(BaseModel):
    """Google Earth Engine authentication configuration."""
    project_id: Optional[str] = None
    service_account: Optional[str] = None
    credentials_file: Optional[str] = None
    authenticated: bool = False

    @classmethod
    def from_env(cls) -> "GEEConfig":
        """Load GEE config from environment variables."""
        return cls(
            project_id=os.environ.get("GEE_PROJECT_ID"),
            service_account=os.environ.get("GEE_SERVICE_ACCOUNT"),
            credentials_file=os.environ.get("GEE_CREDENTIALS_FILE"),
        )

    def has_service_account(self) -> bool:
        return bool(self.credentials_file and os.path.exists(self.credentials_file))

    def use_oauth(self) -> bool:
        return not self.has_service_account()


class GeoStudioConfig(BaseModel):
    """Main configuration for Hermes GeoStudio."""
    
    # Output settings
    output_dir: str = Field(default="./output", alias="GEOSTUDIO_OUTPUT_DIR")
    default_crs: str = Field(default="EPSG:4326", alias="GEOSTUDIO_DEFAULT_CRS")
    
    # Default study area (WKT or GeoJSON)
    default_area: Optional[str] = Field(default=None, alias="GEOSTUDIO_DEFAULT_AREA")
    
    # GEE configuration
    gee: GEEConfig = Field(default_factory=GEEConfig)
    
    # Cartography defaults
    map_width_inches: float = 8.0
    map_height_inches: float = 6.0
    dpi: int = 300
    
    # Performance limits
    max_area_km2: float = 10000.0  # Maximum study area in km²
    max_download_size_mb: int = 500  # Maximum asset download size
    request_timeout_seconds: int = 120
    
    class Config:
        populate_by_name = True
        env_prefix = "GEOSTUDIO_"
        
    @classmethod
    def load(cls) -> "GeoStudioConfig":
        """Load configuration from .env file and environment variables."""
        # Try to load from .env
        env_path = Path(".env")
        if env_path.exists():
            try:
                import dotenv
                dotenv.load_dotenv(env_path)
            except ImportError:
                pass
        
        return cls(**{
            k.replace("GEOSTUDIO_", "").lower(): v
            for k, v in os.environ.items()
            if k.startswith("GEOSTUDIO_")
        })
    
    def ensure_output_dir(self) -> Path:
        """Create output directory if it doesn't exist."""
        output_path = Path(self.output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    
    def get_output_path(self, filename: str) -> Path:
        """Get a full path in the output directory."""
        return self.ensure_output_dir() / filename


# Global config singleton
_config: Optional[GeoStudioConfig] = None


def get_config() -> GeoStudioConfig:
    """Get the global configuration singleton."""
    global _config
    if _config is None:
        _config = GeoStudioConfig.load()
    return _config


def reload_config() -> GeoStudioConfig:
    """Reload configuration from environment."""
    global _config
    _config = GeoStudioConfig.load()
    return _config
