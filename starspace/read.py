import s3fs
import xarray as xr

from starspace.types import SpatialDataTypes


def read_zarr(url: str, object_type: SpatialDataTypes, validate: bool = True) -> xr.DataArray:
    """reader that validates and returns a spatial dataset adhering to a simple spatial schema.

    Parameters
    ----------
    url : str
        local filepath or s3 url pointing to a zarr store.
    validate : bool
        if True, validate the data_array before returning. Raises a ValidationError if the archive
        is invalid.
    object_type : SpatialDataTypes
        Type of data to validate, if requested.

    Returns
    -------
    xr.DataArray:
        DataArray adhering to a simple spatial schema

    """
    if url.startswith("s3://"):
        url = url.replace("s3://", "")
        s3 = s3fs.S3FileSystem()
        store = s3fs.S3Map(root=url, s3=s3, check=False)
        data_set = xr.open_zarr(store=store)

        data_array_name = next(iter(data_set.keys()))
        data_array = data_set[data_array_name]
    else:
        data_array = xr.open_zarr(url)

    if validate:
        object_type.validate(data_array)

    return data_array
