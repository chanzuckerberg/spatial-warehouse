from tempfile import TemporaryDirectory
from pathlib import Path

from starspace.test.util import make_regions
from starspace.classes import Regions
from starspace.constants import REGIONS_NAME


def test_read_write() -> None:
    regions = make_regions()

    with TemporaryDirectory() as dirpath:
        zarr_directory = Path(dirpath)
        regions.save_zarr(url=zarr_directory)

        canada = Regions.load_zarr(url=f"{zarr_directory}.{REGIONS_NAME}.zarr")

        # assert the matrix isn't mutated upon reading
        assert canada.identical(regions)
