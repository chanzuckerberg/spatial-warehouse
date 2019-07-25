import xarray as xr

from .types import SpatialDataTypes


def reorder_fields(data: xr.Dataset, data_type: SpatialDataTypes):
    """order the fields the same way as their order in the enum, keeping a standard order for
    mandatory and optional fields
    """
    raise NotImplementedError


