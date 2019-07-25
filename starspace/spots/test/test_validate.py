from starspace.spots import validate
from starspace._test_utilities import make_spots


def test_validate() -> None:
    ds = make_spots()
    validate(ds)
