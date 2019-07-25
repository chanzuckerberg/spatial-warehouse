from typing import Callable

from enum import Enum

import starspace


class SpatialDataTypes(str, Enum):
    SPOTS = "spots"
    MATRIX = "matrix"
    REGIONS = "regions"

    @property
    def validate(self) -> Callable:
        """return the validator for the given spatial data type"""
        return getattr(starspace, self).validate

    @property
    def write(self) -> Callable:
        return getattr(starspace, self).write

    @property
    def read(self) -> Callable:
        return getattr(starspace, self).read
