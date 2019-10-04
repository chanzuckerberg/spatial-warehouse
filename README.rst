Starspace
=========

.. image:: https://readthedocs.org/projects/starspace/badge/?version=latest
  :target: https://starspace.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. image:: https://travis-ci.com/chanzuckerberg/spatial-warehouse.svg?branch=master
  :target: https://travis-ci.com/chanzuckerberg/spatial-warehouse

Starspace defines a basic, minimal, proof of concept schema for gene or protein expression data
containing spatially localized information. Specifically, it:

1. Defines a standard schema to describe spots, spatial matrices, and cell regions
2. Implements a library that reads and writes files in the defined schema, leveraging the `zarr`_
   container to ensure scalability.
3. To demonstrate the flexibility of the schema, converts data from a variety of published assay
   types, including Spatial Transcriptomics, CODEX, In-situ Sequencing, MERFISH, osmFISH, and
   starMAP
4. Demonstrates how to visualize and interact with these data using common analysis packages, and
   convert the formats into `loom`_ and `anndata`_ objects, for downstream analysis in R and
   Python.
  
See the documentation_ for more info. 

.. _documentation: http://starspace.rtfd.io/

.. _zarr: https://zarr.readthedocs.io/en/stable/
.. _loom: https://linnarssonlab.org/loompy/
.. _anndata: https://anndata.readthedocs.io/en/stable/
