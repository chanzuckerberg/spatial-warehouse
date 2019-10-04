Starspace
=========

Starspace defines a basic, minimal, proof of concept schema for gene or protein expression data
containing spatially localized information. This project accomplishes the following:

1. Defines a standard schema to describe spots, spatial matrices, and cell regions
2. Implements a library that reads and writes files in the defined schema, leveraging the `zarr`_
   container to ensure scalability.
3. To demonstrate the flexibility of the schema, converts data from a variety of published assay
   types, including Spatial Transcriptomics, CODEX, In-situ Sequencing, MERFISH, osmFISH, and
   starMAP
4. Demonstrates how to visualize and interact with these data using common analysis packages, and
   convert the formats into `loom`_ and `anndata`_ objects, for downstream analysis in R and
   Python.

.. _`Spatial transcriptomics`: https://www.spatialresearch.org
.. _`In-situ sequencing`: https://doi.org/10.1038/nmeth.2563
.. _`CODEX`: https://doi.org/10.1016/j.cell.2018.07.010
.. _`MERFISH`: http://zhuang.harvard.edu/merfish.html
.. _`osmFISH`: http://linnarssonlab.org/osmFISH/
.. _`starMAP`: https://www.starmapresources.com/protocol

.. _zarr: https://zarr.readthedocs.io/en/stable/
.. _loom: https://linnarssonlab.org/loompy/
.. _anndata: https://anndata.readthedocs.io/en/stable/


Contents
========

.. toctree::
   :maxdepth: 0
   :caption: Contents:

   schema
   conversion_examples/index
   analysis_examples

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
