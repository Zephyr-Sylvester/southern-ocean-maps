"""Build a polished overview map of the CCAMLR Convention Area.

Uses ccamlrgis (https://github.com/Zephyr-Sylvester/ccamlrgis-py) --
bathymetry, ASD/EEZ boundaries, coastline, a reference grid, a colour
scale and a legend, all in the CCAMLR standard CRS (EPSG:6932).
"""

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap

import ccamlrgis as cg
import ccamlrgis.plot as cgplot

OUT_PATH = "output/ccamlr_overview.png"


def main() -> None:
    bathy = cg.load_bathy(res=5000)
    asds = cg.load_asds()
    eezs = cg.load_eezs()
    coast = cg.load_coastline()
    coast_land = coast[coast["surface"] == "Land"]

    depth_cmap = ListedColormap(cg.DEPTH_COLS)
    depth_norm = BoundaryNorm(cg.DEPTH_CUTS, depth_cmap.N)

    citations = [asds.attrs["citation"], eezs.attrs["citation"], coast.attrs["citation"]]
    fig, ax = cgplot.basemap(figsize=(13, 13), attribution=citations)

    bathy.plot(ax=ax, cmap=depth_cmap, norm=depth_norm, add_colorbar=False)
    ax.set_xlabel("")
    ax.set_ylabel("")
    cgplot.add_colour_scale(ax=ax, cuts=cg.DEPTH_CUTS, cols=cg.DEPTH_COLS, title="Depth (m)", size="4%", pad=0.2)
    cgplot.add_reference_grid(ax=ax, res_lat=10, res_lon=20, lab_lon=0, fontsize=8)

    coast_land.plot(ax=ax, color="dimgrey", linewidth=0)
    eezs.boundary.plot(ax=ax, edgecolor="purple", linewidth=0.9, linestyle="--")
    asds.boundary.plot(ax=ax, edgecolor="black", linewidth=1)
    cgplot.add_labels(ax=ax, mode="auto", layer="ASDs", fontsize=7, fonttype=2, colour="red")

    items = [
        cgplot.LegendItem("ASD / Subarea boundary", shape="line", fill="black", linewidth=1),
        cgplot.LegendItem("EEZ boundary", shape="line", fill="purple", linewidth=1),
        cgplot.LegendItem("Land", shape="rectangle", fill="dimgrey", border="none"),
    ]
    cgplot.add_legend(ax=ax, items=items, title="Legend", loc="upper left", fontsize=9)

    ax.set_title("CCAMLR Convention Area", fontsize=18, fontweight="bold", pad=14)
    fig.savefig(OUT_PATH, dpi=200, bbox_inches="tight")
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
