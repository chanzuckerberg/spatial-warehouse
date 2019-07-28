from typing import Dict

from enum import Enum
from itertools import chain
from pathlib import Path

import numpy as np
import pandas as pd
import xarray as xr
import s3fs

from ._constants import MATRIX_NAME, MATRIX_REQUIRED_REGIONS, MATRIX_REQUIRED_FEATURES, \
MATRIX_AXES, SPOTS_AXES, REQUIRED_ATTRIBUTES, SPOTS_REQUIRED_VARIABLES


# todo figure out how to overwrite existing groups
# todo figure out how to write to s3fs with groups
def _save_zarr(dataset: xr.Dataset, url: str, profile_name: str) -> None:

    if isinstance(url, Path):
        url = str(url)

    if url.startswith("s3://"):

        url = url.replace(" ", '-')
        url = url.rstrip("/")
        url = url.replace("s3://", "")

        if url.count("/") > 1:
            raise ValueError("I haven't figured out how to write groups yet, this will fail.")
        s3 = s3fs.S3FileSystem(profile_name=profile_name)
        root = f"{url}.matrix.zarr"
        store = s3fs.S3Map(root=root, s3=s3, check=False)

        dataset.to_zarr(store=store)

    else:  # assume local
        dataset.to_zarr(url)


def _load_zarr(url: str) -> xr.Dataset:

    if isinstance(url, Path):
        url = str(url)

    if url.startswith("s3://"):
        url = url.replace("s3://", "")
        s3 = s3fs.S3FileSystem()
        store = s3fs.S3Map(root=url, s3=s3, check=False)
        dataset = xr.open_zarr(store=store)
    else:
        dataset = xr.open_zarr(url, chunks=None)  # turn off zarr

    return dataset



class Matrix(xr.DataArray):

    @classmethod
    def from_expression_data(cls, data, coords, dims, attrs, *args, **kwargs):

        # verify that required coordinates are properly formatted
        corrected_coords = {}
        for key, (dim, coord_data) in coords.items():
            if isinstance(dim, Enum):
                dim = dim.value
            if isinstance(key, Enum):
                key = key.value
            if np.asarray(data).dtype == object:
                coord_data = np.array(coord_data, dtype="U")
            corrected_coords[key] = (dim, coord_data)

        # verify that coords contains all required values
        for v in chain(MATRIX_REQUIRED_REGIONS, MATRIX_REQUIRED_FEATURES):
            if v not in corrected_coords.keys():
                raise ValueError(f"missing required coordinate {v}")

        # verify that dimensions are properly formatted
        corrected_dims = tuple([dim.value if isinstance(dim, Enum) else dim for dim in dims])

        if not corrected_dims == tuple(MATRIX_AXES):
            raise ValueError(f"matrix axes must be {tuple(MATRIX_AXES)}.")

        # correct enum attributes
        corrected_attrs = {}
        for key, value in attrs.items():
            if isinstance(key, Enum):
                key = key.value
            corrected_attrs[key] = value

        # verify attributes are present
        for v in REQUIRED_ATTRIBUTES:
            if v not in attrs:
                raise ValueError(f"missing required attribute {v}")

        return cls(
            data=data, dims=corrected_dims, coords=corrected_coords, attrs=attrs, *args, **kwargs
        )

    def save_zarr(self, url: str, profile_name: str = "spacetx") -> None:
        if self.name is None:
            dataset = self.to_dataset(name=MATRIX_NAME)
        else:
            dataset = self.to_dataset()

        _save_zarr(dataset, url, profile_name)

    @classmethod
    def load_zarr(cls, url) -> "Matrix":

        dataset = _load_zarr(url)

        if len(dataset.data_vars) != 1:
            raise ValueError('Given file dataset contains more than one data '
                             'variable. Please read with xarray.open_dataset and '
                             'then select the variable you want.')
        else:
            data_array, = dataset.data_vars.values()

        data_array._file_obj = dataset._file_obj

        # Reset names if they were changed during saving
        # to ensure that we can 'roundtrip' perfectly
        if data_array.name == MATRIX_NAME:
            data_array.name = None

        return cls(data_array)


class Spots(xr.Dataset):

    @classmethod
    def from_spot_data(cls, dataframe: pd.DataFrame, attrs: Dict):

        # verify colnames are strings, not enums
        columns = [c.value if isinstance(c, Enum) else c for c in dataframe.columns]
        dataframe.columns = columns

        # name the index, which will form the dimensions of the dataset
        dataframe.index.name = SPOTS_AXES.SPOTS.value

        # verify attributes are present
        for v in REQUIRED_ATTRIBUTES:
            if v not in attrs:
                raise ValueError(f"missing required attribute {v}.")

        # verify required column information is present
        for v in SPOTS_REQUIRED_VARIABLES:
            if v not in dataframe.columns:
                raise ValueError(f"missing required variable {v}.")

        dataset = cls.from_dataframe(dataframe)
        dataset.attrs = attrs
        return dataset

    def save_zarr(self, url: str, profile_name: str = "spacetx"):
        _save_zarr(self, url, profile_name)

    @classmethod
    def load_zarr(cls, url: str) -> "Spots":
        dataset = _load_zarr(url)
        spots = cls(dataset)
        spots.attrs = dataset.attrs
        return spots


class Regions(xr.Dataset):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save_zarr(self):
        pass

    def load_zarr(self):
        pass
