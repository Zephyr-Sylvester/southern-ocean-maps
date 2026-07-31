"""Shared plotting logic for the planned-PREDYCT-fieldwork figures
(by-country, by-fieldwork-type, and summary). See
make_subarea48_fieldwork_by_country.py, make_subarea48_fieldwork_by_type.py
and make_subarea48_fieldwork_summary.py.

Uses ccamlrgis (https://github.com/Zephyr-Sylvester/ccamlrgis-py).
"""

import textwrap
from collections.abc import Sequence

import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
import pandas as pd

import ccamlrgis as cg
import ccamlrgis.plot as cgplot

CSV_PATH = "data/planned-predyct-fieldwork.csv"
FOOTNOTE_WRAP_WIDTH = 40

# Reference points for named places the CSV gives no coordinates for.
# Manually curated (not derived/eyeballed from other rows) so they stay
# accurate regardless of what else is in the CSV -- Gerlache Strait and
# Elephant Island are charted-position centres; Joinville Island,
# Bransfield Strait and South Orkney Islands are still approximated from
# nearby precise points elsewhere in the CSV and could use the same
# manual treatment if better reference coordinates turn up. These are
# regional approximations, not survey boundaries -- plotted with a
# distinct (open star) marker from precise GPS points.
PLACE_COORDS = {
    "Elephant Island": (-61.1333, -55.1167),  # 61 deg 08' S, 55 deg 07' W
    "Gerlache Strait": (-64.5000, -62.3333),  # 64 deg 30' 00" S, 62 deg 20' 00" W
    "Joinville Island": (-62.685, -54.941),
    "Bransfield Strait": (-63.183, -59.517),
    "South Orkney Islands": (-60.5, -45.9),
}

# Manually curated: distinct named sites close enough together that
# showing each on its own marker adds clutter without adding information
# (e.g. three King George Island tagging sites, a few km apart, on a map
# already showing a dozen other things). Deliberately a manual alias
# table rather than a distance-threshold clustering algorithm, so
# grouping stays predictable and doesn't silently change if a new site
# happens to land near an existing one.
LOCATION_ALIASES = {
    "King George Island 1": "King George Island",
    "King George Island 2": "King George Island",
    "King George Island 3": "King George Island",
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


def _halo_annotate(ax: plt.Axes, text: str, xy: tuple[float, float], color: str) -> None:
    """Number label with a white halo so it stays legible over the
    (often busy) bathymetry/coastline/marker it sits on, instead of
    plain coloured text that can disappear against similarly-coloured
    backgrounds."""
    artist = ax.annotate(
        text,
        xy,
        color=color,
        fontsize=6,
        fontweight="bold",
        xytext=(4, 3),
        textcoords="offset points",
        zorder=6,
    )
    artist.set_path_effects([pe.withStroke(linewidth=2.2, foreground="white")])


def _resolve_place(text: str) -> tuple[float, float] | None:
    """Look up a named place in PLACE_COORDS -- exact match first, then
    substring containment, so e.g. "Shelf region from Gerlache Strait"
    (one half of a range like "Shelf region from Gerlache Strait -
    Elephant Island") still resolves via the "Gerlache Strait" entry
    instead of silently failing to match and never being drawn."""
    text = text.strip()
    if text in PLACE_COORDS:
        return PLACE_COORDS[text]
    for name, coord in PLACE_COORDS.items():
        if name in text:
            return coord
    return None


def plot_row(ax: plt.Axes, row: pd.Series, number: int, label: str) -> str:
    """Draw one CSV row onto ax as a small numbered marker. Returns the
    footnote line ('N. <label> (Location)') listing what that number is,
    for every row -- markers carry a number, not full text, to stay
    legible when several sites cluster close together. `label` is
    whatever the caller wants shown alongside each footnote entry (the
    activity for the by-country figure, activity alone for the by-type
    one, activity + country for the summary)."""
    lat, lon = row["Latitude"], row["Longitude"]
    location = row["Location"]

    if pd.notna(lat) and pd.notna(lon):
        x, y = project(lat, lon)
        ax.scatter([x], [y], marker="o", color="crimson", edgecolor="white", linewidth=0.5, s=42, zorder=5)
        _halo_annotate(ax, str(number), (x, y), color="crimson")
        return f"{number}. {label} ({location})"

    if " - " in location:
        a, b = (p.strip() for p in location.split(" - ", 1))
        pa, pb = _resolve_place(a), _resolve_place(b)
        if pa is not None and pb is not None:
            xa, ya = project(*pa)
            xb, yb = project(*pb)
            ax.plot([xa, xb], [ya, yb], linestyle="--", color="darkorange", linewidth=2, zorder=3)
            mx, my = (xa + xb) / 2, (ya + yb) / 2
            _halo_annotate(ax, str(number), (mx, my), color="darkorange")
            return f"{number}. {label} ({location}, approx.)"

    place = _resolve_place(location)
    if place is not None:
        x, y = project(*place)
        ax.scatter([x], [y], marker="*", facecolor="none", edgecolor="darkorange", linewidth=1.4, s=110, zorder=4)
        _halo_annotate(ax, str(number), (x, y), color="darkorange")
        return f"{number}. {label} ({location}, approx.)"

    return f"{number}. {label} ({location}, no coordinates)"


def group_nearby(df: pd.DataFrame, label_col: str) -> pd.DataFrame:
    """Combine rows that represent the same place into one, so the map
    shows a single labelled marker instead of several stacked/crowded
    ones. Two cases collapse together: rows with no precise coordinates
    that share an exact Location string (e.g. cetacean tagging and
    crabeater seal tagging, both just "Gerlache Strait" -- without this
    they'd draw two translucent markers stacked exactly on top of each
    other, which optically blend into a colour matching neither); and
    precise-coordinate rows whose Location is in LOCATION_ALIASES (e.g.
    three King George Island sites). Genuinely distinct precise points
    with no alias are left untouched.
    """
    df = df.copy()
    df["_place"] = df["Location"].map(lambda loc: LOCATION_ALIASES.get(loc, loc))
    has_coords = df["Latitude"].notna() & df["Longitude"].notna()
    # Only cluster precise points when their Location is aliased to
    # something else -- otherwise every row is its own "cluster" of one
    # and this is a no-op passthrough for genuinely distinct GPS points.
    should_group = ~has_coords | (df["Location"] != df["_place"])

    rows = [row.to_dict() for _, row in df[~should_group].iterrows()]
    for _, sub in df[should_group].groupby("_place", sort=False):
        labels = list(sub[label_col])
        if len(labels) > 1 and len(set(labels)) == 1:
            combined_label = f"{labels[0]} ({len(labels)} sites)"
        else:
            combined_label = "; ".join(labels)
        sub_has_coords = sub["Latitude"].notna() & sub["Longitude"].notna()
        rows.append(
            {
                "Location": sub["_place"].iloc[0],
                label_col: combined_label,
                "Latitude": sub.loc[sub_has_coords, "Latitude"].mean() if sub_has_coords.any() else float("nan"),
                "Longitude": sub.loc[sub_has_coords, "Longitude"].mean() if sub_has_coords.any() else float("nan"),
            }
        )
    return pd.DataFrame(rows)


def build_single_map(
    df: pd.DataFrame,
    label_col: str,
    title: str,
    caption: str,
    out_path: str,
    figsize: tuple[float, float] = (14, 12),
) -> None:
    """One map, every row plotted, no panel grouping -- for a figure
    meant to show *where effort concentrates* across all activities at
    once, not to compare across a country/type dimension. The numbered
    footnote list sits in a sidebar (not below the map) since a
    non-faceted figure can have many more rows to list than any one
    panel in the faceted figures does."""
    df = group_nearby(df, label_col)

    asds = cg.load_asds()
    asds48 = asds[asds["GAR_Short_Label"].isin(["481", "482"])]
    coast = cg.load_coastline()
    coast_land = coast[coast["surface"] == "Land"]
    bounds = tuple(asds48.buffer(30_000).total_bounds)

    fig = plt.figure(figsize=figsize)
    ax = fig.add_axes((0.03, 0.06, 0.62, 0.88))
    draw_basemap(ax, coast_land, asds48, bounds)
    ax.set_title(title, fontsize=15, fontweight="bold")

    footnotes = [plot_row(ax, row, number, row[label_col]) for number, (_, row) in enumerate(df.iterrows(), start=1)]
    wrapped = "\n".join(textwrap.fill(line, width=55, subsequent_indent="    ") for line in footnotes)
    fig.text(0.67, 0.94, wrapped, fontsize=8, va="top", ha="left")
    fig.text(0.5, 0.01, caption, fontsize=8, ha="center", color="dimgrey")
    fig.savefig(out_path, dpi=170)
    print(f"Saved {out_path}")


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
    `label_col` value in the footnote list -- rows representing the same
    place are combined first (see `group_nearby`). `hspace` should scale
    with how many rows the busiest panel's footnote list needs -- a
    panel with many sites needs more room than one with a couple of
    survey areas."""
    asds = cg.load_asds()
    asds48 = asds[asds["GAR_Short_Label"].isin(["481", "482"])]
    coast = cg.load_coastline()
    coast_land = coast[coast["surface"] == "Land"]
    bounds = tuple(asds48.buffer(30_000).total_bounds)

    fig, axes = plt.subplots(*grid_shape, figsize=figsize, gridspec_kw={"hspace": hspace})
    for ax, group in zip(axes.flat, group_order):
        draw_basemap(ax, coast_land, asds48, bounds)
        ax.set_title(group_labels.get(group, group), fontsize=12, fontweight="bold")

        panel_df = group_nearby(df[df[group_col] == group], label_col)
        footnotes = [plot_row(ax, row, number, row[label_col]) for number, (_, row) in enumerate(panel_df.iterrows(), start=1)]
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
