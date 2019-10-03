from enum import Enum

###################################################################################################
# General

_X_REGION = "x_region"
_Y_REGION = "y_region"
_Z_REGION = "z_region"
_REGION_ID = "region_id"
_ROUND = "round"
_CHANNEL = "channel"

_FIELD_OF_VIEW = "fov"

_GENE_NAME = "gene_name"


###################################################################################################
# Attributes

class REQUIRED_ATTRIBUTES(str, Enum):
    ORGANISM = "organism"
    SAMPLE_TYPE = "sample_type"
    ASSAY = "assay"
    YEAR = "year"
    AUTHORS = "authors"


class OPTIONAL_ATTRIBUTES(str, Enum):
    PUBLICATION_NAME = "publication_name"
    PUBLICATION_URL= "publication_url"
    NOTES = "notes"


class ASSAYS(str, Enum):
    MERFISH = "MERFISH"
    ISS = "In-situ Sequencing"
    OSMFISH = "osmFISH"
    CODEX = "CODEX"
    SEQFISH = "SEQFISH"
    SPATIAL_TRANSCRIPTOMICS = "Spatial Transcriptomics"


###################################################################################################
# Spots

SPOTS_NAME = "spots"


class SPOTS_AXES(str, Enum):
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
    RADIUS = "spot_radius"
    FIELD_OF_VIEW = _FIELD_OF_VIEW
    ROUND = _ROUND


###################################################################################################
# Matrix

MATRIX_CHUNK_SIZE = (5000, 1000)

MATRIX_NAME = "matrix"


class MATRIX_REQUIRED_REGIONS(str, Enum):
    REGION_ID = _REGION_ID,
    X_REGION = _X_REGION,
    Y_REGION = _Y_REGION,


class MATRIX_OPTIONAL_REGIONS(str, Enum):
    Z_REGION = _Z_REGION,
    PHYS_ANNOTATION = "physical_annotation"
    BIOL_ANNOTATION = "biological_annotation"
    GROUP_ID = "group_id"
    FIELD_OF_VIEW = _FIELD_OF_VIEW
    AREA_PIXELS = "area_pixels"
    AREA_UM2 = "area_um2"


class MATRIX_AXES(str, Enum):
    REGIONS = "regions"
    FEATURES = "features"


class MATRIX_REQUIRED_FEATURES(str, Enum):
    GENE_NAME = _GENE_NAME


class MATRIX_OPTIONAL_FEATURES(str, Enum):
    ROUND = _ROUND
    CHANNEL = _CHANNEL

class SCANPY_CONSTANTS:
    SPATIAL_LAYOUT = "X_spatial"

###################################################################################################
# Regions

REGIONS_NAME = "regions"


class REGIONS_AXES(str, Enum):
    X_REGION = _X_REGION
    Y_REGION = _Y_REGION
