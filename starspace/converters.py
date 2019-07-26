from enum import Enum
from typing import Dict

import numpy as np
import pandas as pd
import xarray as xr
from itertools import chain

from starspace import SpatialDataTypes
from starspace._constants import MATRIX_REQUIRED_FEATURES, MATRIX_AXES, \
    MATRIX_REQUIRED_REGIONS
from starspace._constants import SPOTS_DIMS


def spots2matrix(dataset: xr.Dataset):
    """convert spots to a matrix, provided required optional annotations are present"""

    for field in chain(MATRIX_REQUIRED_REGIONS, MATRIX_REQUIRED_FEATURES):
        if not hasattr(dataset, field):
            raise ValueError(
                f"dataset must have a '{field}' field to be pivoted to a region x feature matrix"
            )

    data = dataset.to_dataframe()

    grouped = data.groupby([MATRIX_REQUIRED_REGIONS.REGION_ID.value, MATRIX_REQUIRED_FEATURES.GENE_NAME])
    matrix = grouped.count().iloc[:, 0].unstack("gene_name")

    group_columns = [
        MATRIX_REQUIRED_REGIONS.REGION_ID,
        MATRIX_REQUIRED_REGIONS.Y_REGION,
        MATRIX_REQUIRED_REGIONS.X_REGION
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
        data=matrix.values, coords=coords, dims=dims, attrs=dataset.attrs, name="matrix"
    )

    # fill nan with zero
    data_array = data_array.fillna(0)

    # drop features or region missing values in required variables.
    data_array = data_array.where(
        data_array[MATRIX_REQUIRED_FEATURES.GENE_NAME.value] != "nan", drop=True
    )
    data_array = data_array.where(
        data_array[MATRIX_REQUIRED_REGIONS.REGION_ID.value].notnull(), drop=True
    )
    data_array = data_array.where(
        data_array[MATRIX_REQUIRED_REGIONS.X_REGION.value].notnull(), drop=True
    )
    data_array = data_array.where(
        data_array[MATRIX_REQUIRED_REGIONS.Y_REGION.value].notnull(), drop=True
    )

    return data_array


def dataframe2annotated_spots(data: pd.DataFrame, attributes: Dict, validate=True) -> xr.Dataset:
    """intention is to factor out some of the repetitive annoying stuff needed to create the xarray
    object
    """

    data.index.name = SPOTS_DIMS.SPOTS.value

    # ensure attributes are strings
    string_attributes = {}
    for k, v in attributes.items():
        if isinstance(v, Enum):
            v = v.value
        if isinstance(k, Enum):
            k = k.value
        string_attributes[k] = v

    # ensure column names are strings
    data.columns = [c.value if isinstance(c, Enum) else c for c in data.columns]

    dataset = xr.Dataset.from_dataframe(data)
    dataset.attrs = string_attributes

    # ensure gene_name has string dtype
    if dataset[MATRIX_REQUIRED_FEATURES.GENE_NAME].dtype == object:
        dataset[MATRIX_REQUIRED_FEATURES.GENE_NAME].values = np.array(
            dataset[MATRIX_REQUIRED_FEATURES.GENE_NAME], dtype="U"
        )

    if validate:
        SpatialDataTypes.SPOTS.validate(dataset)

    return dataset
