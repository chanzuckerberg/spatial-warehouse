from enum import Enum

_X_REGION = "x_region"
_Y_REGION = "y_region"
_Z_REGION = "z_region"
_REGION_ID = "region_id"

_GENE_NAME = "gene_name"

_MATRIX_CHUNK_SIZE = (5000, 1000)


class REQUIRED_ATTRIBUTES(str, Enum):
    ORGANISM = "organism"
    SAMPLE_TYPE = "sample_type"
    ASSAY = "assay"
    YEAR = "year"
    AUTHORS = "authors"


class OPTIONAL_ATTRIBUTES(str, Enum):
    PUBLICATION_NAME = "publication_name"
    NOTES = "notes"


class ASSAYS(str, Enum):
    MERFISH = "MERFISH"


class SPOTS_DIMS(str, Enum):
    SPOTS = "spots"


class SPOTS_REQUIRED_VARIABLES(str, Enum):
    GENE_NAME = _GENE_NAME
    X_SPOT = "x_spot"
    Y_SPOT = "y_spot"


class SPOTS_OPTIONAL_VARIABLES(str, Enum):
    REGION_ID = _REGION_ID
    X_REGION = _X_REGION
    Y_REGION = _Y_REGION
    Z_REGION = _Z_REGION
    Z_SPOT = "z_spot"
    QUALITY = "spot_quality"


class MATRIX_REQUIRED_REGIONS(str, Enum):
    REGION_ID = _REGION_ID,
    X_REGION = _X_REGION,
    Y_REGION = _Y_REGION,


class MATRIX_OPTIONAL_REGIONS(str, Enum):
    Z_REGION = _Z_REGION,
    ANNOTATION = "annotation"
    GROUP_ID = "group_id"


class MATRIX_AXES(str, Enum):
    REGIONS = "regions"
    FEATURES = "features"


class MATRIX_REQUIRED_FEATURES(str, Enum):
    GENE_NAME = _GENE_NAME


class MATRIX_OPTIONAL_FEATURES(str, Enum):
    pass
