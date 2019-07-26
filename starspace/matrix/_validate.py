from typing import Union
from warnings import warn

import numpy as np
import xarray as xr

from starspace._constants import MATRIX_REQUIRED_REGIONS, MATRIX_OPTIONAL_REGIONS, MATRIX_AXES, \
    MATRIX_REQUIRED_FEATURES, REQUIRED_ATTRIBUTES, ASSAYS
from starspace.exceptions import ValidationError


def validate(data: Union[xr.DataArray]) -> None:
    """

    Parameters
    ----------
    data : Union[xr.DataArray, xr.Dataset]
        data to be validated.

    Raises
    ------
    ValidationError :
        raised if the array does not validate.

    """
    n_failures = 0

    expected_axes = {MATRIX_AXES.REGIONS.value, MATRIX_AXES.FEATURES.value}
    if not set(data.dims) == expected_axes:
        warn(f"Axes must be {expected_axes}, found {set(data.dims)}.")
        n_failures += 1

    required_region_data = {MATRIX_REQUIRED_REGIONS.X_REGION, MATRIX_REQUIRED_REGIONS.Y_REGION}
    missing_region_fields = required_region_data - set(data.coords.keys())
    if missing_region_fields:
        warn(f"Required region metadata fields are missing: {missing_region_fields}")
        n_failures += 1

    required_features_data = {MATRIX_REQUIRED_FEATURES.GENE_NAME}
    missing_features_fields = required_features_data - set(data.coords.keys())
    if missing_features_fields:
        warn(f"Required features metadata fields are missing: {missing_features_fields}")
        n_failures += 1

    for unique_target in [MATRIX_REQUIRED_FEATURES.GENE_NAME]:
        if unique_target in data.coords.keys():
            target_data = data.coords[unique_target]
            n_not_unique = target_data.shape[0] - np.unique(target_data).shape[0]
            if n_not_unique:
                warn(f"{unique_target} field must be unique. "
                     f"Found {n_not_unique} duplicated values")
                n_failures += 1

    missing_attributes = set(REQUIRED_ATTRIBUTES) - set(data.attrs.keys())
    if missing_attributes:
        warn(f"Required attributes are missing: {missing_attributes}")
        n_failures += 1

    assay = data.attrs[REQUIRED_ATTRIBUTES.ASSAY]
    if assay not in set(ASSAYS):
        warn(f"Invalid Assay type: {assay}. Assay must be one of {set(ASSAYS)}")
        n_failures += 1

    if n_failures:
        raise ValidationError(f"{n_failures} validation failures occurred")


