Conversion Scripts
==================

The following directory contains examples to convert author-published results into the spatial
schema. The majority of the scripts are very simple. Each script is named as follows and has
at minimum the following contents:

:code:`<assay_name>_<first_author>_<year>_<journal>_<short_description>.py`


1. Link to original manuscript or preprint, if available, else data attribution information
2. Checklist of available data, including:

  a. cell (or region) x gene count matrix
  b. transcript locations (if appropriate)
  c. cell locations in polygons or masks

4. Instructions to load and convert data into required format, including any information acquired via
   direct communications with authors.
