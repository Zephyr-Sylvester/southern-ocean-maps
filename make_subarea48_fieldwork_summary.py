"""Summary map of planned CCAMLR PREDYCT fieldwork in Subareas 48.1
(Antarctic Peninsula) and 48.2 (South Orkney Islands): one map, every
activity, no faceting by country or type -- the point is to show *where*
effort concentrates, e.g. that Gerlache Strait has both cetacean tagging
and crabeater seal tagging planned, which the by-country/by-type figures
(each activity in its own panel) can't show. Rows representing the same
place are combined into a single labelled marker rather than several
stacked/crowded ones -- see fieldwork_common.group_nearby.

Uses ccamlrgis (https://github.com/Zephyr-Sylvester/ccamlrgis-py).
"""

from fieldwork_common import build_single_map, load_fieldwork

OUT_PATH = "output/subarea48_fieldwork_summary.png"


def main() -> None:
    df = load_fieldwork()
    df["Label"] = df["Activity"] + " -- " + df["Who"]

    build_single_map(
        df,
        label_col="Label",
        title="Planned PREDYCT fieldwork in CCAMLR Subareas 48.1 & 48.2 -- summary",
        caption=(
            "Filled circles: precise coordinates. Open stars/dashed lines: approximate regional placement "
            "(named place, no coordinates supplied); activities/sites sharing a place are listed together "
            "under one marker. Source: data/planned-predyct-fieldwork.csv."
        ),
        out_path=OUT_PATH,
    )


if __name__ == "__main__":
    main()

