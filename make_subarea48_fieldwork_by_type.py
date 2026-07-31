"""Highlight planned CCAMLR PREDYCT fieldwork in Subareas 48.1 (Antarctic
Peninsula) and 48.2 (South Orkney Islands), one panel per fieldwork type
(discipline), from data/planned-predyct-fieldwork.csv.

Uses ccamlrgis (https://github.com/Zephyr-Sylvester/ccamlrgis-py).
"""

from fieldwork_common import build_figure, load_fieldwork

OUT_PATH = "output/subarea48_fieldwork_by_type.png"

TYPE_ORDER = [
    "Krill biomass surveys",
    "Moorings (krill flux)",
    "Fisheries acoustics",
    "Cetacean & whale work",
    "Penguin monitoring & tagging",
    "Seal tagging",
]


def categorize(activity: str) -> str:
    a = activity.lower()
    if "mooring" in a:
        return "Moorings (krill flux)"
    if "krill biomass" in a:
        return "Krill biomass surveys"
    if "fisheries acoustics" in a:
        return "Fisheries acoustics"
    if "penguin" in a:
        return "Penguin monitoring & tagging"
    if "seal" in a:
        return "Seal tagging"
    if "cetacean" in a or "whale" in a:
        return "Cetacean & whale work"
    return "Other"


def main() -> None:
    df = load_fieldwork()
    df["FieldworkType"] = df["Activity"].map(categorize)
    unmatched = df[df["FieldworkType"] == "Other"]
    if not unmatched.empty:
        raise ValueError(f"Uncategorised activities, update categorize(): {unmatched['Activity'].tolist()}")

    build_figure(
        df,
        group_col="FieldworkType",
        group_order=TYPE_ORDER,
        group_labels={},
        label_col="Activity",
        title="Planned PREDYCT fieldwork in CCAMLR Subareas 48.1 & 48.2, by fieldwork type",
        caption=(
            "Filled circles: precise coordinates. Open stars/dashed lines: approximate regional placement "
            "(named place, no coordinates supplied). Source: data/planned-predyct-fieldwork.csv."
        ),
        out_path=OUT_PATH,
        grid_shape=(2, 3),
        figsize=(18, 18),
        hspace=0.5,
        bottom_margin=0.2,
    )


if __name__ == "__main__":
    main()
