from starspace.matrix import validate
from starspace._test_utilities import make_matrix


def test_validate() -> None:
    da = make_matrix()
    validate(da)
