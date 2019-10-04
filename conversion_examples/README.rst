Conversion Scripts
==================

The following directory contains examples to convert author-published results into the spatial
schema. The majority of the scripts are very simple. Each script is named as follows and has
at minimum the following contents:

`<assay_name>_<first_author>_<year>_<journal>_<short_description>.py`

Contents
--------

- Link to original manuscript or preprint, if available, else data attribution information
- Checklist of available data, including:
  - cell (or region) x gene count matrix
  - transcript locations (if appropriate)
  - cell locations in polygons or masks
- Instructions to load and convert data into required format, including any information acquired via
  direct communications with authors.
