"""Professional color palettes for map symbology."""
COLOR_PALETTES = {
    "slope": [
        "#2ca02c",  # 0-2% Datar
        "#8c564b",  # 2-8% Berteluk
        "#ff7f0e",  # 8-15% Curam
        "#e377c2",  # 15-25% Sangat Curam
        "#7f7f7f",  # >25% Tebing
    ],
    "ndvi": [
        "#00441b", "#00a65a", "#9ef011", "#ffffbf",
        "#ffcc40", "#fdae3d", "#f46d43", "#d73027",
    ],
    "landcover": {
        "water": "#1a8cff",
        "forest": "#006400",
        "agriculture": "#daa520",
        "builtup": "#808080",
        "bare": "#d2b48c",
        "grass": "#90EE90",
    },
    "elevation": [
        "#000080", "#0000ff", "#00bfff", "#00ff00",
        "#ffff00", "#ff8c00", "#ff0000", "#ffffff",
    ],
}

DEFAULT_PALETTE = "slope"

def get_palette(name: str) -> list[str]:
    if name in COLOR_PALETTES:
        p = COLOR_PALETTES[name]
        return p if isinstance(p, list) else list(p.values())
    return COLOR_PALETTES.get("slope", [])
