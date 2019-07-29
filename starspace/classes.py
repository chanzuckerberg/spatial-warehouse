from enum import Enum
from itertools import chain
from pathlib import Path
from typing import Dict

import anndata
import dask.array as da
import loompy
import numpy as np
import pandas as pd
import s3fs
import xarray as xr

from .constants import MATRIX_NAME, MATRIX_REQUIRED_REGIONS, MATRIX_REQUIRED_FEATURES, \
    MATRIX_AXES, SPOTS_AXES, REQUIRED_ATTRIBUTES, SPOTS_REQUIRED_VARIABLES, REGIONS_AXES, \
    REGIONS_NAME, SPOTS_NAME


# todo figure out how to overwrite existing groups
# todo figure out how to write to s3fs with groups
def _save_zarr(dataset: xr.Dataset, url: str, profile_name: str, suffix: str) -> None:

    if isinstance(url, Path):
        url = str(url)

    url = url.rstrip("/")

    if url.startswith("s3://"):

        url = url.replace(" ", '-')
        url = url.replace("s3://", "")

        if url.count("/") > 1:
            raise ValueError("I haven't figured out how to write groups yet, this will fail.")
        s3 = s3fs.S3FileSystem(profile_name=profile_name)
        root = f"{url}.{suffix}.zarr"
        store = s3fs.S3Map(root=root, s3=s3, check=False)

        dataset.to_zarr(store=store)

    else:  # assume local
        dataset.to_zarr(f"{url}.{suffix}.zarr")


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

        # convert to dask
        if not isinstance(data, da.core.Array):
            data = da.from_array(data, chunks=(1000, 1000))

        return cls(
            data=data, dims=corrected_dims, coords=corrected_coords, attrs=attrs, *args, **kwargs
        )

    def save_zarr(self, url: str, profile_name: str = "spacetx") -> None:
        if self.name is None:
            dataset = self.to_dataset(name=MATRIX_NAME)
        else:
            dataset = self.to_dataset()

        _save_zarr(dataset, url, profile_name, suffix=MATRIX_NAME)

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

    def to_loom(self, loom_file_name) -> None:
        row_attrs = {k: v.values for (k, v) in self[MATRIX_AXES.REGIONS].coords.items()}
        col_attrs = {k: v.values for (k, v) in self[MATRIX_AXES.FEATURES].coords.items()}
        file_attrs = self.attrs
        loompy.create(
            loom_file_name, self.values, row_attrs, col_attrs, file_attrs=file_attrs
        )

    def to_anndata(self) -> anndata.AnnData:
        row_attrs = {k: v.values for (k, v) in self[MATRIX_AXES.REGIONS].coords.items()}
        col_attrs = {k: v.values for (k, v) in self[MATRIX_AXES.FEATURES].coords.items()}
        file_attrs = self.attrs

        return anndata.AnnData(X=self.values, obs=row_attrs, var=col_attrs, uns=file_attrs)


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
        _save_zarr(self, url, profile_name, suffix=SPOTS_NAME)

    @classmethod
    def load_zarr(cls, url: str) -> "Spots":
        dataset = _load_zarr(url)
        spots = cls(dataset)
        spots.attrs = dataset.attrs
        return spots

    def to_records(self) -> np.array:
        return self.to_dataframe().to_records()

    def to_spatial_matrix(self) -> "Matrix":
        """convert spots to a matrix, provided required optional annotations are present"""

        for field in chain(MATRIX_REQUIRED_REGIONS, MATRIX_REQUIRED_FEATURES):
            if not hasattr(self, field):
                raise ValueError(
                    f"dataset must have a '{field}' field to be pivoted to a region x feature matrix"
                )

        data = self.to_dataframe()

        grouped = data.groupby([MATRIX_REQUIRED_REGIONS.REGION_ID.value, MATRIX_REQUIRED_FEATURES.GENE_NAME])
        matrix = grouped.count().iloc[:, 0].unstack("gene_name")

        group_columns = [
            MATRIX_REQUIRED_REGIONS.REGION_ID,
            MATRIX_REQUIRED_REGIONS.Y_REGION,
            MATRIX_REQUIRED_REGIONS.X_REGION
        ]
        region_ids_map = data.groupby(group_columns).size().reset_index().drop(0, axis=1)

        coords = {
            MATRIX_REQUIRED_FEATURES.GENE_NAME: (MATRIX_AXES.FEATURES.value, matrix.columns),
            MATRIX_REQUIRED_REGIONS.X_REGION: (
                MATRIX_AXES.REGIONS.value,
                region_ids_map.loc[matrix.index, MATRIX_REQUIRED_REGIONS.X_REGION]
            ),
            MATRIX_REQUIRED_REGIONS.Y_REGION: (
                MATRIX_AXES.REGIONS.value,
                region_ids_map.loc[matrix.index, MATRIX_REQUIRED_REGIONS.Y_REGION]
            ),
            MATRIX_REQUIRED_REGIONS.REGION_ID: (MATRIX_AXES.REGIONS.value, matrix.index),
        }
        dims = (MATRIX_AXES.REGIONS.value, MATRIX_AXES.FEATURES.value)

        data_array = xr.DataArray(
            data=matrix.values, coords=coords, dims=dims, attrs=self.attrs, name="matrix"
        )

        # fill nan with zero
        data_array = data_array.fillna(0)

        # drop features or region missing values in required variables.
        data_array = data_array.where(
            data_array[MATRIX_REQUIRED_FEATURES.GENE_NAME.value] != "nan", drop=True
        )
        data_array = data_array.where(
            data_array[MATRIX_REQUIRED_REGIONS.REGION_ID.value].notnull(), drop=True
        )
        data_array = data_array.where(
            data_array[MATRIX_REQUIRED_REGIONS.X_REGION.value].notnull(), drop=True
        )
        data_array = data_array.where(
            data_array[MATRIX_REQUIRED_REGIONS.Y_REGION.value].notnull(), drop=True
        )

        return Matrix(data_array)


class Regions(xr.DataArray):

    @classmethod
    def from_label_image(cls, label_image, dims, attrs, *args, **kwargs):

        if not isinstance(label_image, da.core.Array):
            label_image = da.from_array(label_image, chunks=(1000, 1000))

        # verify that dimensions are properly formatted
        corrected_dims = tuple([dim.value if isinstance(dim, Enum) else dim for dim in dims])

        if not corrected_dims == tuple(REGIONS_AXES):
            raise ValueError(f"matrix axes must be {tuple(REGIONS_AXES)}.")

        # verify attributes are present
        for v in REQUIRED_ATTRIBUTES:
            if v not in attrs:
                raise ValueError(f"missing required attribute {v}")

        return cls(label_image, dims=dims, attrs=attrs)

    def save_zarr(self, url, profile_name: str = "spacetx"):
        if self.name is None:
            dataset = self.to_dataset(name=REGIONS_NAME)
        else:
            dataset = self.to_dataset()

        _save_zarr(dataset, url, profile_name, suffix=REGIONS_NAME)

    @classmethod
    def load_zarr(cls, url):
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
