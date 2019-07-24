from typing import Dict

import xarray as xr
import numpy as np
import pandas as pd

from starspace._constants import *


def make_attributes() -> Dict:
    return {
        REQUIRED_ATTRIBUTES.ASSAY: "MERFISH",
        REQUIRED_ATTRIBUTES.SAMPLE_TYPE: "brains",
        REQUIRED_ATTRIBUTES.AUTHORS: "hannibal lector",
        REQUIRED_ATTRIBUTES.YEAR: 1991,
        REQUIRED_ATTRIBUTES.ORGANISM: "human"
    }


def make_matrix() -> xr.DataArray:

    data = np.array([[0, 1], [1, 0]])

    coords = {
        MATRIX_REQUIRED_FEATURES.GENE_NAME: (MATRIX_AXES.FEATURES.value, ["ACTA", "ACTB"]),
        MATRIX_REQUIRED_REGIONS.X_REGION: (MATRIX_AXES.REGIONS.value, [10, 300]),
        MATRIX_REQUIRED_REGIONS.Y_REGION: (MATRIX_AXES.REGIONS.value, [50, 9e11]),
        MATRIX_REQUIRED_REGIONS.REGION_ID: (MATRIX_AXES.REGIONS.value, [4, 99]),
        MATRIX_OPTIONAL_REGIONS.Z_REGION: (MATRIX_AXES.REGIONS.value, [43, 2]),
        MATRIX_OPTIONAL_REGIONS.GROUP_ID: (MATRIX_AXES.REGIONS.value, [2, 43]),
    }
    dims = tuple(MATRIX_AXES)
    name = "error-free test dataset"
    attrs = make_attributes()

    return xr.DataArray(data=data, coords=coords, dims=dims, name=name, attrs=attrs)


def make_spots() -> xr.Dataset:

    data = {
        SPOTS_REQUIRED_VARIABLES.GENE_NAME: (["ACTA", "ACTB", "ACTA", "ACTB"]),
        SPOTS_REQUIRED_VARIABLES.Y_SPOT: ([0, 1, 0.1, 1e5]),
        SPOTS_REQUIRED_VARIABLES.X_SPOT: ([2, 4, 8, 16]),
        SPOTS_OPTIONAL_VARIABLES.Z_SPOT: ([0.1, 1e-9, 3, 16]),
        SPOTS_OPTIONAL_VARIABLES.REGION_ID: ([0, 1, 2, 3]),
        SPOTS_OPTIONAL_VARIABLES.Y_REGION: ([100, 1, 0.1, 1e5]),
        SPOTS_OPTIONAL_VARIABLES.X_REGION: ([2, 3, 8, 16]),
        SPOTS_OPTIONAL_VARIABLES.Z_REGION: ([0.7, 1e-9, 3, 16]),
    }
    df = pd.DataFrame(data)
    df.index.name = SPOTS_DIMS.SPOTS
    attrs = make_attributes()
    ds = xr.Dataset.from_dataframe(df)
    ds.attrs = attrs

    return ds

