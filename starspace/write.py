import xarray as xr
import s3fs


def write_zarr(dataset: xr.Dataset, name: str) -> None:
    """write a spatial dataset to a zarr store

    Parameters
    ----------
    dataset : xr.Dataset
        the xarray dataset to write. Must have a name
    name : str
        name of the Dataset. Will be used as the name of the zarr archive. Any spaces will be
        replaced with dashes.

    """

    name = name.replace(" ", '-')
    if not name.endswith("/"):
        name += "/"

    s3 = s3fs.S3FileSystem(profile_name="spacetx")  # TODO generalize
    store = s3fs.S3Map(root=f'starfish.data.output-warehouse/{name}.zarr', s3=s3, check=False)
    dataset.to_zarr(store=store)
