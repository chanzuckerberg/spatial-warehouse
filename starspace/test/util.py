from typing import Dict, Tuple, List

import xarray as xr
import numpy as np
import pandas as pd

from starspace._constants import *
from starspace.classes import Matrix, Spots


def make_attributes() -> Dict:
    return {
        REQUIRED_ATTRIBUTES.ASSAY: "MERFISH",
        REQUIRED_ATTRIBUTES.SAMPLE_TYPE: "brains",
        REQUIRED_ATTRIBUTES.AUTHORS: "hannibal lector",
        REQUIRED_ATTRIBUTES.YEAR: 1991,
        REQUIRED_ATTRIBUTES.ORGANISM: "human"
    }


def make_matrix_coords() -> Dict[Enum, Tuple[Enum, List]]:
    coords = {
        MATRIX_REQUIRED_FEATURES.GENE_NAME: (MATRIX_AXES.FEATURES, ["ACTA", "ACTB"]),
        MATRIX_REQUIRED_REGIONS.X_REGION: (MATRIX_AXES.REGIONS, [10, 300]),
        MATRIX_REQUIRED_REGIONS.Y_REGION: (MATRIX_AXES.REGIONS, [50, 9e11]),
        MATRIX_REQUIRED_REGIONS.REGION_ID: (MATRIX_AXES.REGIONS, [4, 99]),
        MATRIX_OPTIONAL_REGIONS.Z_REGION: (MATRIX_AXES.REGIONS, [43, 2]),
        MATRIX_OPTIONAL_REGIONS.GROUP_ID: (MATRIX_AXES.REGIONS, [2, 43]),
    }
    return coords


def make_matrix() -> Matrix:

    data = np.array([[0, 1], [1, 0]])
    coords = make_matrix_coords()
    dims = tuple(MATRIX_AXES)
    attrs = make_attributes()

    return Matrix.from_expression_data(data=data, coords=coords, dims=dims, attrs=attrs)


def make_spots() -> Spots:

    data = pd.DataFrame({
        SPOTS_REQUIRED_VARIABLES.GENE_NAME: (["ACTA", "ACTB", "ACTA", "ACTB"]),
        SPOTS_REQUIRED_VARIABLES.Y_SPOT: ([0, 1, 0.1, 1e5]),
        SPOTS_REQUIRED_VARIABLES.X_SPOT: ([2, 4, 8, 16]),
        SPOTS_OPTIONAL_VARIABLES.Z_SPOT: ([0.1, 1e-9, 3, 16]),
        SPOTS_OPTIONAL_VARIABLES.REGION_ID: ([0, 1, 2, 3]),
        SPOTS_OPTIONAL_VARIABLES.Y_REGION: ([100, 1, 0.1, 1e5]),
        SPOTS_OPTIONAL_VARIABLES.X_REGION: ([2, 3, 8, 16]),
        SPOTS_OPTIONAL_VARIABLES.Z_REGION: ([0.7, 1e-9, 3, 16]),
    })
    attrs = make_attributes()
    return Spots.from_spot_data(data, attrs)
