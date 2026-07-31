"""Shared plotting logic for the planned-PREDYCT-fieldwork figures
(by-country and by-fieldwork-type). See make_subarea48_fieldwork_by_country.py
and make_subarea48_fieldwork_by_type.py.

Uses ccamlrgis (https://github.com/Zephyr-Sylvester/ccamlrgis-py).
"""

import textwrap
from collections.abc import Sequence

import matplotlib.pyplot as plt
import pandas as pd

import ccamlrgis as cg
import ccamlrgis.plot as cgplot

CSV_PATH = "data/planned-predyct-fieldwork.csv"
FOOTNOTE_WRAP_WIDTH = 40

# Reference points for named places the CSV gives no coordinates for,
# reused from precise coordinates elsewhere in the same CSV where
# possible (Gerlache Strait, Joinville Island, Bransfield Strait via the
# Southern Bransfield Strait moorings, South Orkney Islands via the
# Coronation/Monroe Island cluster) -- Elephant Island is the one place
# not otherwise pinned down in the data, using its standard charted
# position. These are regional approximations, not survey boundaries --
# plotted with a distinct (open star) marker from precise GPS points.
PLACE_COORDS = {
    "Elephant Island": (-61.133, -55.183),
    "Gerlache Strait": (-64.3185261, -61.8927691),
    "Joinville Island": (-62.685, -54.941),
    "Bransfield Strait": (-63.183, -59.517),
    "South Orkney Islands": (-60.5, -45.9),
}


def load_fieldwork() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Location"] = df["Location"].str.strip()
    df["Who"] = df["Who"].str.strip()
    df["Activity"] = df["Activity"].str.strip()
    return df


def project(lat: float, lon: float) -> tuple[float, float]:
    out = cg.project_data(pd.DataFrame({"Lat": [lat], "Lon": [lon]}), names_in=["Lat", "Lon"], append=False)
    return float(out["X"].iloc[0]), float(out["Y"].iloc[0])


def draw_basemap(ax: plt.Axes, coast_land, asds48, bounds: tuple[float, float, float, float]) -> None:
    cgplot.basemap(ax=ax, xlim=(bounds[0], bounds[2]), ylim=(bounds[1], bounds[3]))
    coast_land.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.2)
    asds48.boundary.plot(ax=ax, edgecolor="black", linewidth=1)
    cgplot.add_reference_grid(ax=ax, bounds=bounds, res_lat=2, res_lon=5, fontsize=6, linewidth=0.5)


def plot_row(ax: plt.Axes, row: pd.Series, number: int, label: str) -> str:
    """Draw one CSV row onto ax as a small numbered marker. Returns the
    footnote line ('N. <label> (Location)') listing what that number is,
    for every row -- markers carry a number, not full text, to stay
    legible when several sites cluster close together. `label` is
    whatever the caller wants shown alongside each footnote entry (the
    activity for the by-country figure, activity + country for the
    by-type one, so the country isn't lost just because it's no longer
    the grouping dimension)."""
    lat, lon = row["Latitude"], row["Longitude"]
    location = row["Location"]
    label_kwargs = dict(fontsize=6, fontweight="bold", xytext=(4, 3), textcoords="offset points", zorder=6)

    if pd.notna(lat) and pd.notna(lon):
        x, y = project(lat, lon)
        ax.scatter([x], [y], marker="o", color="crimson", edgecolor="white", linewidth=0.5, s=42, zorder=5)
        ax.annotate(str(number), (x, y), color="crimson", **label_kwargs)
        return f"{number}. {label} ({location})"

    if " - " in location:
        a, b = (p.strip() for p in location.split(" - ", 1))
        pa, pb = PLACE_COORDS.get(a), PLACE_COORDS.get(b)
        if pa is not None and pb is not None:
            xa, ya = project(*pa)
            xb, yb = project(*pb)
            ax.plot([xa, xb], [ya, yb], linestyle="--", color="dimgrey", linewidth=1.5, zorder=3)
            mx, my = (xa + xb) / 2, (ya + yb) / 2
            ax.annotate(str(number), (mx, my), color="dimgrey", **label_kwargs)
            return f"{number}. {label} ({location}, approx.)"

    place = PLACE_COORDS.get(location)
    if place is not None:
        x, y = project(*place)
        ax.scatter([x], [y], marker="*", facecolor="none", edgecolor="dimgrey", linewidth=1, s=90, zorder=4)
        ax.annotate(str(number), (x, y), color="dimgrey", **label_kwargs)
        return f"{number}. {label} ({location}, approx.)"

    return f"{number}. {label} ({location}, no coordinates)"


def build_figure(
    df: pd.DataFrame,
    group_col: str,
    group_order: Sequence[str],
    group_labels: dict[str, str],
    label_col: str,
    title: str,
    caption: str,
    out_path: str,
    grid_shape: tuple[int, int],
    figsize: tuple[float, float],
    hspace: float = 0.7,
    bottom_margin: float = 0.12,
) -> None:
    """Shared figure builder: one panel per `group_col` value (in
    `group_order`), each row within that group labelled with its
    `label_col` value in the footnote list. `hspace` should scale with
    how many rows the busiest panel's footnote list needs -- a panel
    with many sites (e.g. 10+ tagging locations) needs more room than
    one with a couple of survey areas."""
    asds = cg.load_asds()
    asds48 = asds[asds["GAR_Short_Label"].isin(["481", "482"])]
    coast = cg.load_coastline()
    coast_land = coast[coast["surface"] == "Land"]
    bounds = tuple(asds48.buffer(30_000).total_bounds)

    fig, axes = plt.subplots(*grid_shape, figsize=figsize, gridspec_kw={"hspace": hspace})
    for ax, group in zip(axes.flat, group_order):
        draw_basemap(ax, coast_land, asds48, bounds)
        ax.set_title(group_labels.get(group, group), fontsize=12, fontweight="bold")

        footnotes = [
            plot_row(ax, row, number, row[label_col])
            for number, (_, row) in enumerate(df[df[group_col] == group].iterrows(), start=1)
        ]
        wrapped = "\n".join(
            textwrap.fill(line, width=FOOTNOTE_WRAP_WIDTH, subsequent_indent="   ") for line in footnotes
        )
        ax.text(
            0.02, -0.03, wrapped, transform=ax.transAxes, fontsize=6.5, color="black", va="top", ha="left"
        )

    fig.suptitle(title, fontsize=17, fontweight="bold")
    fig.text(0.5, 0.005, caption, fontsize=8, ha="center", color="dimgrey")
    # Not tight_layout: it sizes purely from the Axes bounding boxes and has
    # no idea the footnote text (placed via ax.text in axes-fraction
    # coordinates, extending below each Axes) exists at all -- it reliably
    # warns about this and won't reserve room for it. Explicit margins
    # instead; `bottom` needs to comfortably fit the busiest panel's
    # wrapped footnote list, not just look right for the others.
    fig.subplots_adjust(left=0.03, right=0.99, top=0.94, bottom=bottom_margin, hspace=hspace, wspace=0.25)
    fig.savefig(out_path, dpi=180)
    print(f"Saved {out_path}")
