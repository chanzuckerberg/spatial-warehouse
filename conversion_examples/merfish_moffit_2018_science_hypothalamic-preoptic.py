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
import requests
from io import BytesIO

import dask.array as da
import numpy as np
import pandas as pd

import starspace
from starspace.constants import *

response = requests.get(
    "https://d24h2xsgaj29mf.cloudfront.net/raw/merfish_moffit_2018_science_hypothalamic-preoptic/"
    "Moffitt_and_Bambah-Mukku_et_al_merfish_all_cells.csv"
)
data = pd.read_csv(BytesIO(response.content), header=0)

name = "merfish moffit 2018 science hypothalamic preoptic"

###################################################################################################
# This data file is a cell x gene expression matrix that contains additional metadata as columns
# of the matrix. Extract those extra columns and clean up the data file.
annotation = np.array(data["Cell_class"], dtype="U")
group_id = np.array(data["Neuron_cluster_ID"], dtype="U")
x = data["Centroid_X"]
y = data["Centroid_Y"]
region_id = np.array(data["Cell_ID"], dtype="U")

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

attrs = {
    REQUIRED_ATTRIBUTES.ASSAY: ASSAYS.MERFISH,
    REQUIRED_ATTRIBUTES.SAMPLE_TYPE: "hypothalamic pre-optic nucleus",
    REQUIRED_ATTRIBUTES.AUTHORS: [
        "Jeffrey R. Moffitt", "Dhananjay Bambah-Mukku", "Stephen W. Eichhorn", "Eric Vaughn",
        "Karthik Shekhar", "Julio D. Perez", "Nimrod D. Rubinstein", "Junjie Hao", "Aviv Regev",
        "Catherine Dulac", "Xiaowei Zhuang"
    ],
    REQUIRED_ATTRIBUTES.YEAR: 2018,
    REQUIRED_ATTRIBUTES.ORGANISM: "mouse",
    OPTIONAL_ATTRIBUTES.PUBLICATION_NAME: (
        "Molecular, spatial, and functional single-cell profiling of the hypothalamic preoptic "
        "region"
    ),
    OPTIONAL_ATTRIBUTES.PUBLICATION_URL: "https://science.sciencemag.org/content/362/6416/eaau5324",
}

###################################################################################################
# Create the chunked dataset.

chunk_data = da.from_array(expression_data.values, chunks=MATRIX_CHUNK_SIZE)

###################################################################################################
# Wrap the dask array in an xarray, adding the metadata fields as "coordinates".

# convert columns with object dtype into fixed-length strings

coords = {
    MATRIX_REQUIRED_FEATURES.GENE_NAME: (MATRIX_AXES.FEATURES.value, gene_name),
    MATRIX_REQUIRED_REGIONS.X_REGION: (MATRIX_AXES.REGIONS.value, x),
    MATRIX_REQUIRED_REGIONS.Y_REGION: (MATRIX_AXES.REGIONS.value, y),
    MATRIX_REQUIRED_REGIONS.REGION_ID: (MATRIX_AXES.REGIONS.value, region_id),
    MATRIX_OPTIONAL_REGIONS.GROUP_ID: (MATRIX_AXES.REGIONS.value, group_id),
    MATRIX_OPTIONAL_REGIONS.TYPE_ANNOTATION: (MATRIX_AXES.REGIONS.value, annotation)
}
dims = (MATRIX_AXES.REGIONS.value, MATRIX_AXES.FEATURES.value)
matrix = starspace.Matrix.from_expression_data(
    data=chunk_data, coords=coords, dims=dims, name=name, attrs=attrs
)

s3_url = "s3://starfish.data.output-warehouse/merfish-moffit-2018-science-hypothalamic-preoptic"
url = "merfish-moffit-2018-science-hypothalamic-preoptic"
matrix.save_zarr(url=url)
