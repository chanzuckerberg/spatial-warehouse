"""
Molecular, spatial, and functional single-cell profiling of the hypothalamic preoptic region
============================================================================================

Jeffrey R. Moffitt, Dhananjay Bambah-Mukku, Stephen W. Eichhorn, Eric Vaughn, Karthik Shekhar,
Julio D. Perez, Nimrod D. Rubinstein, Junjie Hao, Aviv Regev, Catherine Dulac, Xiaowei Zhuang

This publication can be found at https://science.sciencemag.org/content/362/6416/eaau5324 and the
data referenced below can be downloaded from https://datadryad.org/handle/10255/dryad.192644

Checklist:
- [ ] point locations
- [ ] cell locations
- [x] cell x gene expression matrix

Load the data
-------------
"""

import os

import dask.array as da
import pandas as pd
import xarray as xr

import starspace.read
from starspace.matrix.constants import CHUNK_SIZE, AXES, REGIONS, FEATURES, ASSAYS, ATTRIBUTES
from starspace.types import SpatialDataTypes

directory = (
    "~/google_drive/czi/spatial-approaches/in-situ-transcriptomics/MERFISH/"
    "2018_moffit_science_hypothalamic-pre-optic"
)
data = pd.read_csv(os.path.join(directory, "Moffitt_and_Bambah-Mukku_et_al_merfish_all_cells.csv"))
name = "merfish moffit 2018 science hypothalamic preoptic"

###################################################################################################
# This data file is a cell x gene expression matrix that contains additional metadata as columns
# of the matrix. Extract those extra columns and clean up the data file.

annotation = data["Cell_class"]
group_id = data["Neuron_cluster_ID"]
x = data["Centroid_X"]
y = data["Centroid_Y"]
region_id = data["Cell_ID"]

unstructured_field_names = ["Animal_ID", "Animal_sex", "Behavior", "Bregma"]
unstructured_metadata = data[unstructured_field_names]
non_expression_fields = (
        unstructured_field_names
        + ["Cell_class", "Neuron_cluster_ID", "Centroid_X", "Centroid_Y", "Cell_ID"]
)
expression_data = data.drop(non_expression_fields, axis=1)
gene_name = [v.lower() for v in expression_data.columns]

###################################################################################################
# Write down some important metadata from the publication.

authors = ["Jeffrey R. Moffitt", "Dhananjay Bambah-Mukku", "Stephen W. Eichhorn", "Eric Vaughn",
           "Karthik Shekhar", "Julio D. Perez", "Nimrod D. Rubinstein", "Junjie Hao", "Aviv Regev",
           "Catherine Dulac", "Xiaowei Zhuang"]
year = 2018
organism = "mouse"
sample_type = "hypothalamic pre-optic nucleus"
publication_name = ("Molecular, spatial, and functional single-cell profiling of the hypothalamic "
                    "preoptic region")
assay = ASSAYS.MERFISH
attrs = {
    ATTRIBUTES.ASSAY: assay,
    ATTRIBUTES.SAMPLE_TYPE: sample_type,
    ATTRIBUTES.AUTHORS: authors,
    ATTRIBUTES.YEAR: year,
    ATTRIBUTES.ORGANISM: organism
}

###################################################################################################
# Create the chunked dataset.

chunk_data = da.from_array(expression_data.values, chunks=CHUNK_SIZE)

###################################################################################################
# Wrap the dask array in an xarray, adding the metadata fields as "coordinates".

coords = {
    FEATURES.GENE_NAME: (AXES.FEATURES, gene_name),
    REGIONS.X: (AXES.REGIONS, x),
    REGIONS.Y: (AXES.REGIONS, y),
    REGIONS.ID: (AXES.REGIONS, region_id),
    REGIONS.GROUP_ID: (AXES.REGIONS, group_id),
    REGIONS.ANNOTATION: (AXES.REGIONS, annotation)
}
dims = (AXES.REGIONS.value, AXES.FEATURES.value)
data_array = xr.DataArray(data=chunk_data, coords=coords, dims=dims, name=name, attrs=attrs)

###################################################################################################
# Convert to an xarray dataset and write to a zarr archive on s3.

dataset = data_array.to_dataset()
starspace.write_zarr(dataset, name, SpatialDataTypes.MATRIX)

ds = starspace.read.read_zarr(
    "s3://starfish.data.output-warehouse/merfish-moffit-2018-science-hypothalamic-preoptic.zarr/"
)
