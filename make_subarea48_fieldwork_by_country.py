"""Highlight planned CCAMLR PREDYCT fieldwork in Subareas 48.1 (Antarctic
Peninsula) and 48.2 (South Orkney Islands), one panel per leading
country/collaboration, from data/planned-predyct-fieldwork.csv.

Uses ccamlrgis (https://github.com/Zephyr-Sylvester/ccamlrgis-py).
"""

from fieldwork_common import build_figure, load_fieldwork

OUT_PATH = "output/subarea48_fieldwork_by_country.png"

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


def main() -> None:
    df = load_fieldwork()
    build_figure(
        df,
        group_col="Who",
        group_order=WHO_ORDER,
        group_labels=WHO_LABELS,
        label_col="Activity",
        title="Planned PREDYCT fieldwork in CCAMLR Subareas 48.1 & 48.2, by lead country/collaboration",
        caption=(
            "Filled circles: precise coordinates. Open stars/dashed lines: approximate regional placement "
            "(named place, no coordinates supplied). Source: data/planned-predyct-fieldwork.csv."
        ),
        out_path=OUT_PATH,
        grid_shape=(2, 5),
        figsize=(24, 13),
    )


if __name__ == "__main__":
    main()
