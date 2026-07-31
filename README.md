# southern-ocean-maps

Original figures built with [ccamlrgis](https://github.com/Zephyr-Sylvester/ccamlrgis-py),
the Python port of the CCAMLR `CCAMLRGIS` R package. Not affiliated with
CCAMLR; authoritative data remains at https://gis.ccamlr.org/.

## Setup

```
mamba env create -f environment.yml
mamba activate southern-ocean-maps
python make_overview_map.py
```

(`environment.yml` installs `ccamlrgis` in editable mode from `../ccamlrgis-py`
-- both repos need to be sibling directories.)

## Figures

### CCAMLR Convention Area overview

`make_overview_map.py` -> `output/ccamlr_overview.png`

Full-resolution bathymetry (`load_bathy`), ASD/Subarea boundaries and
labels, EEZ boundaries, coastline, a reference grid, a non-overlapping
colour scale, a custom shape legend, and a rule-9 data-source/projection
attribution caption -- all in the CCAMLR standard CRS (EPSG:6932).

![CCAMLR Convention Area overview](output/ccamlr_overview.png)
