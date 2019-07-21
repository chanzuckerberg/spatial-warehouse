import s3fs
import xarray as xr

from .validate import validate_data_array


def read_zarr(s3_url: str, validate=True) -> xr.DataArray:
    """reader that validates and returns a spatial dataset adhering to a simple spatial schema.

    Parameters
    ----------
    s3_url : str
        s3 url pointing to a zarr store.
    validate : bool
        if True, validate the data_array before returning. Raises a ValidationError if the archive
        is invalid.

    Returns
    -------
    xr.DataArray:
        DataArray adhering to a simple spatial schema

    """
    # TODO open local, too
    s3_url = s3_url.replace("s3://", "")
    s3 = s3fs.S3FileSystem()
    store = s3fs.S3Map(root=s3_url, s3=s3, check=False)
    data_set = xr.open_zarr(store=store)

    data_array_name = next(iter(data_set.keys()))
    data_array = data_set[data_array_name]

    if validate:
        validate_data_array(data_array)

    return data_array
