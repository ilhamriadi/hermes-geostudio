"""GEE authentication and connection management."""
import os
from typing import Optional, Any
import ee
from rich.console import Console
console = Console()
_init_state: dict[str, Any] = {"initialized": False, "method": None, "project": None}

def is_initialized() -> bool:
    return _init_state["initialized"]

def get_init_method() -> Optional[str]:
    return _init_state["method"]

def authenticate_gee() -> dict[str, Any]:
    console.print("[bold yellow]Starting GEE OAuth authentication...[/bold yellow]")
    try:
        ee.Authenticate()
        ee.Initialize()
        _init_state.update({"initialized": True, "method": "oauth", "project": "earthengine-public"})
        return {"success": True, "method": "oauth", "message": "GEE authenticated via OAuth.", "project": "earthengine-public"}
    except Exception as e:
        return {"success": False, "method": "oauth", "error": str(e), "message": f"OAuth failed: {e}"}

def initialize_gee(service_account_key_path: Optional[str] = None) -> dict[str, Any]:
    cred_path = service_account_key_path or os.environ.get("GEE_CREDENTIALS_FILE")
    if cred_path and os.path.exists(cred_path):
        try:
            credentials = ee.ServiceAccountCredentials("", cred_path)
            project = os.environ.get("GEE_PROJECT_ID", "earthengine-public")
            ee.Initialize(credentials=credentials, project=project)
            _init_state.update({"initialized": True, "method": "service_account", "project": project})
            return {"success": True, "method": "service_account", "project": project, "message": f"GEE initialized from {cred_path}"}
        except Exception as e:
            return {"success": False, "method": "service_account", "error": str(e)}
    if not _init_state["initialized"]:
        return authenticate_gee()
    return {"success": True, "method": _init_state["method"], "project": _init_state["project"], "message": "Already initialized"}

def check_connection() -> dict[str, Any]:
    if not is_initialized():
        result = initialize_gee()
        if not result["success"]:
            return result
    try:
        test_fc = ee.FeatureCollection("USDOS/LSIB_LASTED_POP")
        count = test_fc.size().getInfo()
        return {"success": True, "connected": True, "method": _init_state["method"],
                "project": _init_state["project"], "test_result": f"Connected. Sample count: {count}"}
    except Exception as e:
        return {"success": False, "connected": False, "error": str(e)}
