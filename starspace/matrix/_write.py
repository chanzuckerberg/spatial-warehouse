from typing import Union

import xarray as xr
import s3fs

from starspace.types import SpatialDataTypes


def write(
        data: xr.DataArray,
        url: str,
        object_type: SpatialDataTypes,
        validate: bool=True
) -> None:
    """write a spatial dataset to a zarr store

    Parameters
    ----------
    dataset : Union[xr.Dataset, xr.DataArray]
        the xarray dataset to write. Must have a name
    url : str
        name of the Dataset. Will be used as the name of the zarr archive. Any spaces will be
        replaced with dashes.
    object_type : SpatialDataTypes
        type of data object being written.
    validate : bool
        if True, validate the data object prior to writing

    """

    if validate:
        object_type.validate(data)

    if isinstance(data, xr.DataArray):
        attrs = data.attrs
        data = data.to_dataset()
        data.attrs = attrs

    if url.startswith("s3://"):

        url = url.replace(" ", '-')
        url = url.rstrip("/")

        s3 = s3fs.S3FileSystem(profile_name="spacetx")  # TODO generalize
        store = s3fs.S3Map(
            root=f'starfish.data.output-warehouse/{url}/{object_type.name}.zarr',
            s3=s3, check=False
        )

        data.to_zarr(store=store)

    else:  # assume local
        data.to_zarr(url)
