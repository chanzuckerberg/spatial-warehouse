from warnings import warn

import xarray as xr
from .constants import ASSAYS, ATTRIBUTES, AXES, FEATURES, REGIONS
from .exceptions import ValidationError


def validate_data_array(data_array: xr.DataArray) -> None:
    """

    Parameters
    ----------
    data_array : xr.DataArray
        array to be validated.

    Raises
    ------
    ValidationError :
        raised if the array does not validate.

    """
    n_failures = 0

    expected_axes = (AXES.REGIONS, AXES.FEATURES)
    if not data_array.dims == expected_axes:
        warn(f"Axes must be {expected_axes}, found {data_array.dims}.")
        n_failures += 1

    required_region_data = {REGIONS.ANNOTATION, REGIONS.GROUP_ID, REGIONS.ID, REGIONS.X, REGIONS.Y}
    missing_region_fields = required_region_data - set(data_array.coords.keys())
    if missing_region_fields:
        warn(f"Required region metadata fields are missing: {missing_region_fields}")
        n_failures += 1

    required_features_data = {FEATURES.GENE_NAME}
    missing_features_fields = required_features_data - set(data_array.coords.keys())
    if missing_features_fields:
        warn(f"Required features metadata fields are missing: {missing_features_fields}")
        n_failures += 1

    required_attributes = {
        ATTRIBUTES.ORGANISM, ATTRIBUTES.YEAR, ATTRIBUTES.AUTHORS, ATTRIBUTES.ASSAY
    }
    missing_attributes = required_attributes - set(data_array.attrs.keys())
    if missing_attributes:
        warn(f"Required attributes are missing: {missing_attributes}")
        n_failures += 1

    assay = data_array.attrs[ATTRIBUTES.ASSAY]
    if assay not in ASSAYS.__members__:
        warn(f"Invalid Assay type: {assay}. Assay must be one of {ASSAYS.__members__}")
        n_failures += 1
    if n_failures:
        raise ValidationError(f"{n_failures} validation failures occurred")


