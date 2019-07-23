"""
Spatially resolved, highly multiplexed RNA profiling in single cells
============================================================================================

Kok Hao Chen, Alistair N. Boettiger, Jeffrey R. Moffitt, Siyuan Wang, Xiaowei Zhuang

This publication can be found at https://science.sciencemag.org/content/348/6233/aaa6090 and the
data referenced below can be downloaded from

Checklist:
- [x] point locations
- [ ] cell locations
- [x] cell x gene expression matrix (derivable)

Load the data
-------------
"""

import os

import pandas as pd
import xarray as xr

import starspace
from starspace._constants import (
    SPOTS_REQUIRED_VARIABLES, MATRIX_REQUIRED_REGIONS, REQUIRED_ATTRIBUTES, ASSAYS, MATRIX_REQUIRED_FEATURES,
    MATRIX_AXES, SPOTS_OPTIONAL_VARIABLES, SPOTS_DIMS
)
from starspace.types import SpatialDataTypes

directory = (
    "~/google_drive/czi/spatial-approaches/in-situ-transcriptomics/MERFISH/"
    "2015_chen_science_merfish"
)
data = pd.read_excel(os.path.join(directory, "140genesData.xlsx"))
name = "merfish chen 2015 science imr90"

###################################################################################################
# This data file is a cell x gene expression matrix that contains additional metadata as columns
# of the matrix. Extract those extra columns and clean up the data file.

# map column names to schema

column_map = {
    "RNACentroidX": SPOTS_REQUIRED_VARIABLES.X_SPOT,
    "RNACentroidY": SPOTS_REQUIRED_VARIABLES.Y_SPOT,
    "cellID": "per_slice_cell_id",  # this is not unique experiment-wide
    "CellPositionX": SPOTS_OPTIONAL_VARIABLES.X_REGION,
    "CellPositionY": SPOTS_OPTIONAL_VARIABLES.Y_REGION,
    "geneName": SPOTS_REQUIRED_VARIABLES.GENE_NAME,
    "experiment": "experiment",
    "library": "library",
    "intCodeword": "int_codeword",
    "isCorrectedMatch": "is_corrected_match",
    "isExactMatch": "is_exact_match"
}
columns = [column_map[c] for c in data.columns]
data.columns = columns

# demonstrate that cellID is not unique:
group_columns = (
    "per_slice_cell_id",
    SPOTS_OPTIONAL_VARIABLES.Y_REGION,
    SPOTS_OPTIONAL_VARIABLES.X_REGION,
)

# group by the columns, use size to run a no-op aggregation routine, then drop the size column
# (labeled zero)
not_unique = data.groupby(group_columns).size().reset_index().drop(0, axis=1)

assert_cols = ["per_slice_cell_id"]
assert not_unique[assert_cols].drop_duplicates().shape != not_unique[assert_cols].shape

# fix region ids so that they uniquely identify cells across the experiment.
group_columns = (
    "experiment", "library", "per_slice_cell_id",
    SPOTS_OPTIONAL_VARIABLES.Y_REGION, SPOTS_OPTIONAL_VARIABLES.X_REGION
)
region_ids_map = data.groupby(group_columns).size().reset_index().drop(0, axis=1)

assert_cols = ["per_slice_cell_id", "library", "experiment"]
assert region_ids_map[assert_cols].drop_duplicates().shape == region_ids_map[assert_cols].shape

# map each region to a unique identifier and add it to the data frame
region_ids_map = region_ids_map.drop(
    [SPOTS_OPTIONAL_VARIABLES.Y_REGION, SPOTS_OPTIONAL_VARIABLES.X_REGION], axis=1
)
region_ids_map = region_ids_map.reset_index().set_index(assert_cols)

region_ids = region_ids_map.loc[pd.MultiIndex.from_frame(data[assert_cols])]
data[SPOTS_OPTIONAL_VARIABLES.REGION_ID] = region_ids.values

###################################################################################################
# Write down some important metadata from the publication.
authors = (
    "Kok Hao Chen", "Alistair N. Boettiger", "Jeffrey R. Moffitt", "Siyuan Wang", "Xiaowei Zhuang"
)
year = 2015
organism = "human"
sample_type = "IMR90 lung cell line"
publication_name = "Spatially resolved, highly multiplexed RNA profiling in single cells"
assay = ASSAYS.MERFISH.value
notes = "cellID field from author data renamed per_slice_cell_id to reflect stored data"
attrs = {
    REQUIRED_ATTRIBUTES.ASSAY: assay,
    REQUIRED_ATTRIBUTES.SAMPLE_TYPE: sample_type,
    REQUIRED_ATTRIBUTES.AUTHORS: authors,
    REQUIRED_ATTRIBUTES.YEAR: year,
    REQUIRED_ATTRIBUTES.ORGANISM: organism
}

#TODO figure out how to convert to dask intermediate; should be possible.

###################################################################################################
# convert the dataframe into an xarray dataset

data.index.name = SPOTS_DIMS.SPOTS
dataset = xr.Dataset.from_dataframe(data)

# overwrite attrs
dataset.attrs = attrs

###################################################################################################
# Write the data to zarr on s3

starspace.write_zarr(dataset, 'chen2.zarr', SpatialDataTypes.SPOTS)

# verify the dataset is readable.
starspace.read.read_zarr(
    "s3://starfish.data.output-warehouse/merfish-chen-2015-science-hypothalamic-preoptic/"
    "spots.zarr/",
    object_type=SpatialDataTypes.SPOTS
)

###################################################################################################
# Convert the xarray dataset to a matrix.

data = dataset.to_dataframe()

# TODO conversion of points to matrix may be something that we want to generalize and save to the
#  package
grouped = data.groupby([SPOTS_OPTIONAL_VARIABLES.REGION_ID.value, MATRIX_REQUIRED_FEATURES.GENE_NAME])
matrix = grouped.count().iloc[:, 0].unstack("gene_name")

group_columns = [
    SPOTS_OPTIONAL_VARIABLES.REGION_ID,
    SPOTS_OPTIONAL_VARIABLES.Y_REGION,
    SPOTS_OPTIONAL_VARIABLES.X_REGION
]
region_ids_map = data.groupby(group_columns).size().reset_index().drop(0, axis=1)

coords = {
    MATRIX_REQUIRED_FEATURES.GENE_NAME: (MATRIX_AXES.FEATURES.value, matrix.columns),
    MATRIX_REQUIRED_REGIONS.X_REGION: (
        MATRIX_AXES.REGIONS.value,
        region_ids_map.loc[matrix.index, MATRIX_REQUIRED_REGIONS.X_REGION]
    ),
    MATRIX_REQUIRED_REGIONS.Y_REGION: (
        MATRIX_AXES.REGIONS.value,
        region_ids_map.loc[matrix.index, MATRIX_REQUIRED_REGIONS.Y_REGION]
    ),
    MATRIX_REQUIRED_REGIONS.REGION_ID: (MATRIX_AXES.REGIONS.value, matrix.index),
}
dims = (MATRIX_AXES.REGIONS.value, MATRIX_AXES.FEATURES.value)

data_array = xr.DataArray(
    data=matrix.values, coords=coords, dims=dims, name=name, attrs=dataset.attrs
)

attrs = data_array.attrs
dataset = data_array.to_dataset()
dataset.attrs = attrs
starspace.write_zarr(
    dataset,
    url="s3://starfish.data.output-warehouse/merfish-chen-2015-science-hypothalamic-preoptic/" 
        "matrix.zarr/",
    object_type=SpatialDataTypes.MATRIX,
)
