from tempfile import TemporaryDirectory
from pathlib import Path

from starspace.test.util import make_spots


def test_read_write() -> None:
    spots = make_spots()

    with TemporaryDirectory() as dirpath:
        zarr_directory = Path(dirpath) / "archive.zarr"
        spots.save_zarr(url=zarr_directory)

        see_spot_run = spots.load_zarr(zarr_directory)

        # assert that data aren't mutated upon reading
        assert see_spot_run.identical(spots)
