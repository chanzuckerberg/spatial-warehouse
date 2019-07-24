from pathlib import Path
from typing import Union

import xarray as xr
import s3fs

from ._validate import validate


def write(
        data: xr.DataArray,
        url: Union[Path, str],
        profile_name: str = "spacetx",
        validate_data: bool = True
) -> None:
    """write a spatial data array to a zarr store

    Parameters
    ----------
    data : xr.DataArray
        the xarray dataset to write. Must have a name
    url : Union[Path, str]
        name of the Dataset. Will be used as the name of the zarr archive. Any spaces will be
        replaced with dashes.
    profile_name : str
        s3 profile to use for permissions
    validate_data : bool
        if True, validate the data object prior to writing

    """
    if isinstance(url, Path):
        url = str(url)

    if validate_data:
        validate(data)

    # attrs are lost in data array conversion, so stick them to the dataset that's created
    attrs = data.attrs
    data = data.to_dataset()
    data.attrs = attrs

    if url.startswith("s3://"):

        url = url.replace(" ", '-')
        url = url.rstrip("/")

        s3 = s3fs.S3FileSystem(profile_name=profile_name)  # TODO generalize (anon=True)
        store = s3fs.S3Map(
            root=f'starfish.data.output-warehouse/{url}/matrix.zarr',
            s3=s3, check=False
        )

        data.to_zarr(store=store)

    else:  # assume local
        data.to_zarr(url)


def read(url: Union[Path, str], validate_data: bool = True) -> xr.DataArray:
    """reader that validates and returns a spatial dataset adhering to a simple spatial schema.

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
    xr.DataArray:
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

    # reconstruct the array
    variables = iter(data_set.keys())
    data_array_name = next(variables)
    coords = list(variables)
    data_array = xr.DataArray(
        data=data_set[data_array_name],
        coords=data_set[coords],
        dims=data_set.dims
    )
    del data_array.attrs["coordinates"]

    if validate_data:
        validate(data_array)

    return data_array
