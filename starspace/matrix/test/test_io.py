from tempfile import TemporaryDirectory
from pathlib import Path

import numpy as np

from starspace._test_utilities import make_matrix
from starspace.matrix._io import read, write


def test_read_write() -> None:
    matrix = make_matrix()

    with TemporaryDirectory() as dirpath:
        zarr_directory = Path(dirpath) / "archive.zarr"
        write(matrix, url=zarr_directory, validate_data=True)

        the_matrix_reloaded = read(zarr_directory, validate_data=True)

        # assert the matrix isn't mutated upon reading
        assert np.array_equal(the_matrix_reloaded, matrix)
        for c in matrix.coords.keys():
            assert np.array_equal(the_matrix_reloaded.coords[c], matrix.coords[c])
        for a in matrix.attrs.keys():
            assert matrix.attrs[a] == the_matrix_reloaded.attrs[a]
