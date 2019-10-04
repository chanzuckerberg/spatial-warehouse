"""
Deep Profiling of Mouse Splenic Architecture with CODEX Multiplexed Imaging
===========================================================================

Yury Goltsev, Nikolay Samusik, Julia Kennedy-Darling, Salil Bhate, Matthew Hale, Gustavo Vazquez,
Sarah Black, Garry P. Nolan

The data can be downloaded here: http://welikesharingdata.blob.core.windows.net/forshare/index.html
and the paper is available here: https://doi.org/10.1016/j.cell.2018.07.010
"""
from pathlib import Path
from collections import defaultdict

import pandas as pd
import numpy as np

import starspace
from starspace.constants import *

path_dir = Path("~/google_drive/czi/spatial-approaches/proteomics/codex")
expression_file = path_dir / "Suppl.Table2.CODEX_paper_MRLdatasetexpression.csv"

data = pd.read_csv(expression_file)

attributes = {
    REQUIRED_ATTRIBUTES.ASSAY: ASSAYS.CODEX,
    REQUIRED_ATTRIBUTES.SAMPLE_TYPE: "spleen",
    REQUIRED_ATTRIBUTES.AUTHORS: [
        "Yury Goltsev", "Nikolay Samusik", "Julia Kennedy-Darling", "Salil Bhate", "Matthew Hale",
        "Gustavo Vazquez", "Sarah Black", "Garry P. Nolan"
    ],
    REQUIRED_ATTRIBUTES.YEAR: 2018,
    REQUIRED_ATTRIBUTES.ORGANISM: "mouse",
    OPTIONAL_ATTRIBUTES.PUBLICATION_URL: "https://doi.org/10.1016/j.cell.2018.07.010",
    OPTIONAL_ATTRIBUTES.PUBLICATION_NAME:
        "Deep Profiling of Mouse Splenic Architecture with CODEX Multiplexed Imaging",
}

dims = tuple(MATRIX_AXES)

x = data["X.X"]
y = data["Y.Y"]
z = data["Z.Z"]
group = data["niche cluster ID"]
metadata_col = data["sample_Xtile_Ytile"]
type_annotation = data["Imaging phenotype cluster ID"]

data = data.drop(
    ["X.X", "Y.Y", "Z.Z", "sample_Xtile_Ytile", "niche cluster ID", "Imaging phenotype cluster ID"],
    axis=1
)

additional_metadata = defaultdict(list)
for i, v in enumerate(metadata_col):
    sample_type, fov_x, fov_y = v.split('_')
    additional_metadata["sample_type"].append(sample_type)
    additional_metadata["fov_x"].append(int(fov_x.strip("X")))
    additional_metadata["fov_y"].append(int(fov_y.strip("Y")))
additional_metadata = pd.DataFrame(additional_metadata)

coords = {
    MATRIX_REQUIRED_REGIONS.REGION_ID: (MATRIX_AXES.REGIONS, data.index),
    MATRIX_REQUIRED_FEATURES.GENE_NAME: (MATRIX_AXES.FEATURES, data.columns),
    MATRIX_REQUIRED_REGIONS.X_REGION: (MATRIX_AXES.REGIONS, x),
    MATRIX_REQUIRED_REGIONS.Y_REGION: (MATRIX_AXES.REGIONS, y),
    MATRIX_OPTIONAL_REGIONS.Z_REGION: (MATRIX_AXES.REGIONS, z),
    MATRIX_OPTIONAL_REGIONS.GROUP_ID: (MATRIX_AXES.REGIONS, group),
    MATRIX_OPTIONAL_REGIONS.TYPE_ANNOTATION: (MATRIX_AXES.REGIONS, type_annotation),
    "fov_x": (MATRIX_AXES.REGIONS, additional_metadata["fov_x"]),
    "fov_y": (MATRIX_AXES.REGIONS, additional_metadata["fov_y"]),
    "sample_type": (MATRIX_AXES.REGIONS, additional_metadata["sample_type"])
}

matrix = starspace.Matrix.from_expression_data(data.values, coords, dims, attributes)
# s3_url = ("s3://starfish.data.output-warehouse/codex_goltsev_2018_cell_spleen/")
url = ("codex_goltsev_2018_cell_spleen/")
matrix.save_zarr(url=url)
