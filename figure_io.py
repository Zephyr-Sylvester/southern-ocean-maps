"""Shared figure-saving helper. Every figure in this repo saves as both
PNG (for inline embedding, e.g. in README.md) and PDF (vector, for
print/zoom) from the same `out_path`, which should end in .png."""

from pathlib import Path

import matplotlib.pyplot as plt


def save_fig(fig: plt.Figure, out_path: str, **kwargs: object) -> None:
    png_path = Path(out_path).with_suffix(".png")
    pdf_path = Path(out_path).with_suffix(".pdf")
    fig.savefig(png_path, **kwargs)
    fig.savefig(pdf_path, **kwargs)
    print(f"Saved {png_path} and {pdf_path}")
