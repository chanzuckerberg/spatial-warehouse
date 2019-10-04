.. _schema:

Schema
======

Starspace defines three basic object types that describe the features extracted from a typical
spatial experiment: spots, cells, and cell x gene expression matrices. It defines standard
terminology to describe the basic spatial information for each object, allowing interoperability
between data from different assays, and, if such a standard form were adopted, would make these
data accessible to tool chains.

This repository intentionally describes a schema but *not a format* -- these data could be defined
in any number of ways. This repository chooses to use zarr

Spots
-----

Spots is a tabular data table, where each record describes a spot. The columns of this table have
three required fields and several standardized, but optional fields:

.. literalinclude:: ../schema/spots/spots_columns.json
  :language: JSON

The axes of this object can optionally be named:

.. literalinclude:: ../schema/spots/spots_axes.json
  :language: JSON

Regions
-------

Regions stores a label image. Each pixel belonging to a cell is encoded using the same integer
value. Each sequential object is labeled with the next smallest integer. Such an image allows
for each intersection of spots and cells to create a count matrix, but such an image can also be
overlaid on image data to verify that cells were properly segmented.

The axes of this object can optionally be named:

.. literalinclude:: ../schema/regions/regions_axes.json
  :language: JSON

Matrix
------

The matrix file is a traditional region x feature expression matrix. Its values can contain either
count data (e.g. spots) or continuous data (e.g. protein intensities). Regions can represent cells,
anatomical areas, or stereotyped super-cellular areas, like those measured by slide-seq or spatial
transcriptomics. features can be protein or rna abundances, or counts of other anatomical structures
aggregated over regions.

The matrix stores metadata for each region that describe characteristics of the region:

.. literalinclude:: ../schema/matrix/matrix_regions.json
  :language: JSON

The matrix also stores metadata that describe the features:

.. literalinclude:: ../schema/matrix/matrix_features.json
  :language: JSON

The axes of the matrix can optionally be named:

.. literalinclude:: ../schema/matrix/matrix_axes.json
  :language: JSON
