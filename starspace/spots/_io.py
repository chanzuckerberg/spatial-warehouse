from pathlib import Path
from typing import Union

import xarray as xr
import s3fs

from ._validate import validate


def write(
        data: xr.Dataset,
        url: Union[Path, str],
        profile_name: str = "spacetx",
        validate_data: bool = True
) -> None:
    """Write spot data to a zarr store.

    Parameters
    ----------
    data : xr.Dataset
        the dataset to write.
    url : Union[Path, str]
        file path or url to the zarr archive. Any spaces will be replaced with dashes.
    profile_name : str
        s3 profile to use for permissions
    validate_data : bool
        if True, validate the data object prior to writing

    """
    if isinstance(url, Path):
        url = str(url)

    if validate_data:
        validate(data)

    if url.startswith("s3://"):

        url = url.replace(" ", "-")
        url = url.rstrip("/")
        url = url.replace("s3://", "")

        if url.count("/") > 1:
            raise ValueError("I haven't figured out how to write groups yet, this will fail.")
        s3 = s3fs.S3FileSystem(profile_name=profile_name)
        root = f"{url}.spots.zarr"
        store = s3fs.S3Map(root=root, s3=s3, check=False)

        data.to_zarr(store=store)

    else:  # assume local
        data.to_zarr(url)


def read(url: Union[Path, str], validate_data: bool = True) -> xr.Dataset:
    """Reader that validates and returns a spatial dataset adhering to a simple spatial schema.

    Parameters
    ----------
    url : Union[Path, str]
        local filepath or s3 url pointing to a zarr store.
    validate_data : bool
        if True, validate the data_array before returning. Raises a ValidationError if the archive
        is invalid.
    object_type : SpatialDataTypes
        Type of data to validate, if requested.

    Returns
    -------
    xr.Dataset:
        DataArray adhering to a simple spatial schema

    """
    if isinstance(url, Path):
        url = str(url)

    if url.startswith("s3://"):
        url = url.replace("s3://", "")
        s3 = s3fs.S3FileSystem()
        store = s3fs.S3Map(root=url, s3=s3, check=False)
        data_set = xr.open_zarr(store=store)
    else:
        data_set = xr.open_zarr(url, chunks=None)  # turn off zarr

    if validate_data:
        validate(data_set)

    return data_set
