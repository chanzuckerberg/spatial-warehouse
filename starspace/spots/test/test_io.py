from tempfile import TemporaryDirectory
from pathlib import Path

from starspace._test_utilities import make_spots
from starspace.spots._io import read, write


def test_read_write() -> None:
    spots = make_spots()

    with TemporaryDirectory() as dirpath:
        zarr_directory = Path(dirpath) / "archive.zarr"
        write(spots, url=zarr_directory, validate_data=True)

        see_spot_run = read(zarr_directory, validate_data=True)

        # assert that data aren't mutated upon reading
        assert see_spot_run.identical(spots)
