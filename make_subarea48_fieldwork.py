"""Highlight planned CCAMLR PREDYCT fieldwork in Subareas 48.1 (Antarctic
Peninsula) and 48.2 (South Orkney Islands), one panel per leading
country/collaboration, from data/planned-predyct-fieldwork.csv.

Uses ccamlrgis (https://github.com/Zephyr-Sylvester/ccamlrgis-py).
"""

import textwrap

import matplotlib.pyplot as plt
import pandas as pd

import ccamlrgis as cg
import ccamlrgis.plot as cgplot

FOOTNOTE_WRAP_WIDTH = 40

CSV_PATH = "data/planned-predyct-fieldwork.csv"
OUT_PATH = "output/subarea48_fieldwork_by_country.png"

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

WHO_ORDER = [
    "Germany",
    "Peru",
    "Norway",
    "Norway/HUBOcean, Chile, (China)",
    "USA",
    "USA, UK",
    "Australia (Angus Henderson)",
    "Argentina/Uruguay",
    "?",
    "France",
]
WHO_LABELS = {
    "Norway/HUBOcean, Chile, (China)": "Norway / HUBOcean / Chile / China",
    "Australia (Angus Henderson)": "Australia",
    "?": "Unknown / TBD",
}


def load_fieldwork() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH, encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Location"] = df["Location"].str.strip()
    df["Who"] = df["Who"].str.strip()
    return df


def project(lat: float, lon: float) -> tuple[float, float]:
    out = cg.project_data(pd.DataFrame({"Lat": [lat], "Lon": [lon]}), names_in=["Lat", "Lon"], append=False)
    return float(out["X"].iloc[0]), float(out["Y"].iloc[0])


def draw_basemap(ax: plt.Axes, coast_land, asds48, bounds: tuple[float, float, float, float]) -> None:
    cgplot.basemap(ax=ax, xlim=(bounds[0], bounds[2]), ylim=(bounds[1], bounds[3]))
    coast_land.plot(ax=ax, color="lightgrey", edgecolor="black", linewidth=0.2)
    asds48.boundary.plot(ax=ax, edgecolor="black", linewidth=1)
    cgplot.add_reference_grid(ax=ax, bounds=bounds, res_lat=2, res_lon=5, fontsize=6, linewidth=0.5)


def plot_row(ax: plt.Axes, row: pd.Series, number: int) -> str:
    """Draw one CSV row onto ax as a small numbered marker. Returns the
    footnote line ('N. Activity (Location)') listing what that number is,
    for every row -- markers carry a number, not full text, to stay
    legible when several sites cluster close together."""
    lat, lon = row["Latitude"], row["Longitude"]
    location = row["Location"]
    activity = row["Activity"]
    label_kwargs = dict(fontsize=6, fontweight="bold", xytext=(4, 3), textcoords="offset points", zorder=6)

    if pd.notna(lat) and pd.notna(lon):
        x, y = project(lat, lon)
        ax.scatter([x], [y], marker="o", color="crimson", edgecolor="white", linewidth=0.5, s=42, zorder=5)
        ax.annotate(str(number), (x, y), color="crimson", **label_kwargs)
        return f"{number}. {activity} ({location})"

    if " - " in location:
        a, b = (p.strip() for p in location.split(" - ", 1))
        pa, pb = PLACE_COORDS.get(a), PLACE_COORDS.get(b)
        if pa is not None and pb is not None:
            xa, ya = project(*pa)
            xb, yb = project(*pb)
            ax.plot([xa, xb], [ya, yb], linestyle="--", color="dimgrey", linewidth=1.5, zorder=3)
            mx, my = (xa + xb) / 2, (ya + yb) / 2
            ax.annotate(str(number), (mx, my), color="dimgrey", **label_kwargs)
            return f"{number}. {activity} ({location}, approx.)"

    place = PLACE_COORDS.get(location)
    if place is not None:
        x, y = project(*place)
        ax.scatter([x], [y], marker="*", facecolor="none", edgecolor="dimgrey", linewidth=1, s=90, zorder=4)
        ax.annotate(str(number), (x, y), color="dimgrey", **label_kwargs)
        return f"{number}. {activity} ({location}, approx.)"

    return f"{number}. {activity} ({location}, no coordinates)"


def main() -> None:
    df = load_fieldwork()

    asds = cg.load_asds()
    asds48 = asds[asds["GAR_Short_Label"].isin(["481", "482"])]
    coast = cg.load_coastline()
    coast_land = coast[coast["surface"] == "Land"]
    bounds = tuple(asds48.buffer(30_000).total_bounds)

    fig, axes = plt.subplots(2, 5, figsize=(24, 13), gridspec_kw={"hspace": 0.7})
    for ax, who in zip(axes.flat, WHO_ORDER):
        draw_basemap(ax, coast_land, asds48, bounds)
        ax.set_title(WHO_LABELS.get(who, who), fontsize=11, fontweight="bold")

        footnotes = [
            plot_row(ax, row, number) for number, (_, row) in enumerate(df[df["Who"] == who].iterrows(), start=1)
        ]
        wrapped = "\n".join(
            textwrap.fill(line, width=FOOTNOTE_WRAP_WIDTH, subsequent_indent="   ") for line in footnotes
        )
        ax.text(
            0.02,
            -0.03,
            wrapped,
            transform=ax.transAxes,
            fontsize=6,
            color="black",
            va="top",
            ha="left",
        )

    fig.suptitle(
        "Planned PREDYCT fieldwork in CCAMLR Subareas 48.1 & 48.2, by lead country/collaboration",
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.5,
        0.005,
        "Filled circles: precise coordinates. Open stars/dashed lines: approximate regional placement "
        "(named place, no coordinates supplied). Source: data/planned-predyct-fieldwork.csv.",
        fontsize=8,
        ha="center",
        color="dimgrey",
    )
    fig.tight_layout(rect=(0, 0.02, 1, 0.96))
    fig.savefig(OUT_PATH, dpi=180, bbox_inches="tight")
    print(f"Saved {OUT_PATH}")


if __name__ == "__main__":
    main()
