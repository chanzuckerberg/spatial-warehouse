from typing import Union
from warnings import warn

import numpy as np
import pandas as pd
import xarray as xr

from starspace._constants import (
    ASSAYS,
    REQUIRED_ATTRIBUTES,
    SPOTS_DIMS,
    SPOTS_REQUIRED_VARIABLES,
    SPOTS_OPTIONAL_VARIABLES
)
from starspace.exceptions import ValidationError


def validate(data_set: Union[xr.Dataset, pd.DataFrame]) -> None:
    """validate spot data

    Parameters
    ----------
    data_set : Union[xr.Dataset, pd.DataFrame],
        spot data to be validated.

    Raises
    ------
    ValidationError :
        raised if the array does not validate.

    """
    n_failures = 0

    # these are interchangeable, use the dataset because it supports annotations
    if isinstance(data_set, pd.DataFrame):
        data_set: xr.Dataset = xr.Dataset.from_dataframe(data_set)

    expected_axes = (SPOTS_DIMS.SPOTS,)
    if not tuple(data_set.dims) == expected_axes:
        warn(f"Axes must be {expected_axes}, found {data_set.dims}.")
        n_failures += 1

    required_fields = set(SPOTS_REQUIRED_VARIABLES)
    missing_region_fields = required_fields - set(data_set.variables.keys())
    if missing_region_fields:
        warn(f"Missing required columns: {missing_region_fields}")
        n_failures += 1

    for unique_target in (SPOTS_REQUIRED_VARIABLES.GENE_NAME, SPOTS_OPTIONAL_VARIABLES.REGION_ID):
        if unique_target in data_set.coords.keys():
            data = data_set.coords[unique_target]
            n_not_unique = data.shape[0] - np.unique(data).shape[0]
            if n_not_unique:
                warn(f"{unique_target} field must be unique. Found {n_not_unique} duplicated values")
                n_failures += 1

    missing_attributes = set(REQUIRED_ATTRIBUTES) - set(data_set.attrs.keys())
    if missing_attributes:
        warn(f"Required attributes are missing: {missing_attributes}")
        n_failures += 1

    assay = data_set.attrs[REQUIRED_ATTRIBUTES.ASSAY]
    if assay not in ASSAYS.__members__:
        warn(f"Invalid Assay type: {assay}. Assay must be one of {ASSAYS.__members__}")
        n_failures += 1

    if n_failures:
        raise ValidationError(f"{n_failures} validation failures occurred")
