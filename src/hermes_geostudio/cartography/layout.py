"""Create professional map layouts with matplotlib."""
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from typing import Any, Optional
import numpy as np

LAYOUT_SIZES = {
    "A4_portrait": (210, 297),
    "A4_landscape": (297, 210),
    "A3_portrait": (297, 420),
    "A3_landscape": (420, 297),
}

def create_map_layout(
    map_data_path: str,
    output_path: str,
    size: str = "A4_landscape",
    title: str = "Peta Analisis Geospasial",
    legend_items: Optional[list[dict]] = None,
    source: str = "",
    date: str = "",
    crs: str = "EPSG:4326",
    dpi: int = 300,
) -> dict:
    try:
        width_inches, height_inches = LAYOUT_SIZES[size]
        fig_width = width_inches / dpi * 2
        fig_height = height_inches / dpi * 2

        fig, ax = plt.subplots(1, 1, figsize=(fig_width, fig_height), dpi=dpi)

        # Load and display map data
        import rasterio
        with rasterio.open(map_data_path) as src:
            data = src.read(1)
            im = ax.imshow(data, cmap="terrain", extent=src.bounds[:4])
            ax.set_title(title, fontsize=14, fontweight="bold", pad=20)

            # Colorbar
            cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            cbar.set_label("Nilai", fontsize=10)

        # Legend
        if legend_items:
            patches = [mpatches.Patch(color=c, label=l) for c, l in legend_items]
            ax.legend(handles=patches, loc="lower right", fontsize=8, framealpha=0.9)

        # Metadata box
        meta_text = f"CRS: {crs}"
        if source: meta_text += f"\nSumber: {source}"
        if date: meta_text += f"\nTanggal: {date}"
        ax.text(0.02, 0.98, meta_text, transform=ax.transAxes, fontsize=8,
                verticalalignment="top", bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

        ax.set_aspect("auto")
        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi, bbox_inches="tight", facecolor="white")
        plt.close()

        file_size_kb = os.path.getsize(output_path) / 1024 if os.path.exists(output_path) else 0
        return {
            "success": True, "output_path": output_path,
            "size_inches": (width_inches, height_inches), "dpi": dpi,
            "file_size_kb": round(file_size_kb, 1), "title": title,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
