"""Build a zoomed-in map of CCAMLR Subarea 48 (Antarctic Peninsula /
Scotia Sea), using ccamlrgis (https://github.com/Zephyr-Sylvester/ccamlrgis-py).
"""

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap

import ccamlrgis as cg
import ccamlrgis.plot as cgplot

OUT_PATH = "output/subarea48_overview.png"
SUBAREA_48_CODES = ["481", "482", "483", "484", "485", "486"]


def main() -> None:
    asds_all = cg.load_asds()
    asds48 = asds_all[asds_all["GAR_Short_Label"].isin(SUBAREA_48_CODES)]
    eezs = cg.load_eezs()
    coast = cg.load_coastline()
    coast_land = coast[coast["surface"] == "Land"]

    bounds = tuple(asds48.buffer(50_000).total_bounds)
    bathy = cg.load_bathy(res=2500)
    bathy48 = bathy.rio.clip_box(*bounds)

    depth_cmap = ListedColormap(cg.DEPTH_COLS)
    depth_norm = BoundaryNorm(cg.DEPTH_CUTS, depth_cmap.N)

    citations = [asds_all.attrs["citation"], eezs.attrs["citation"], coast.attrs["citation"]]
    fig, ax = cgplot.basemap(figsize=(11, 11), attribution=citations)

    bathy48.plot(ax=ax, cmap=depth_cmap, norm=depth_norm, add_colorbar=False)
    ax.set_xlabel("")
    ax.set_ylabel("")
    cgplot.add_colour_scale(ax=ax, cuts=cg.DEPTH_CUTS, cols=cg.DEPTH_COLS, title="Depth (m)", size="4%", pad=0.2)
    cgplot.add_reference_grid(ax=ax, bounds=bounds, res_lat=5, res_lon=10, fontsize=8)

    coast_land.plot(ax=ax, color="dimgrey", linewidth=0)
    eezs.boundary.plot(ax=ax, edgecolor="purple", linewidth=1, linestyle="--")
    asds48.boundary.plot(ax=ax, edgecolor="black", linewidth=1.3)
    cgplot.add_labels(ax=ax, mode="auto", layer="ASDs", fontsize=10, fonttype=2, colour="red")

    ax.set_xlim(bounds[0], bounds[2])
    ax.set_ylim(bounds[1], bounds[3])

    items = [
        cgplot.LegendItem("Subarea / Division boundary", shape="line", fill="black", linewidth=1),
        cgplot.LegendItem("EEZ boundary", shape="line", fill="purple", linewidth=1),
        cgplot.LegendItem("Land", shape="rectangle", fill="dimgrey", border="none"),
    ]
    cgplot.add_legend(ax=ax, items=items, title="Legend", loc="upper left", fontsize=9)

    ax.set_title("CCAMLR Subarea 48", fontsize=18, fontweight="bold", pad=14)
    fig.savefig(OUT_PATH, dpi=200, bbox_inches="tight")
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
