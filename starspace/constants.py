import json
import os

from enum import Enum
from pathlib import Path

###################################################################################################
# Load schema

directory = Path(os.path.dirname(os.path.abspath(__file__))).parent


###################################################################################################
# General

_ROUND = "round"
_CHANNEL = "channel"

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

with open(directory / "schema/spots/spots_axes.json", "rb") as f:
    _spots_axes = json.load(f)

with open(directory / "schema/spots/spots_columns.json", "rb") as f:
    _spots_columns = json.load(f)

SPOTS_NAME = "spots"

class SPOTS_AXES(str, Enum):
    SPOTS = _spots_axes[1]["name"]


class SPOTS_REQUIRED_VARIABLES(str, Enum):
    GENE_NAME = _spots_columns[0]["name"]
    Y_SPOT = _spots_columns[1]["name"]
    X_SPOT = _spots_columns[2]["name"]


class SPOTS_OPTIONAL_VARIABLES(str, Enum):
    Z_SPOT = _spots_columns[3]["name"]
    REGION_ID = _spots_columns[4]["name"]
    Z_REGION = _spots_columns[5]["name"]
    Y_REGION = _spots_columns[6]["name"]
    X_REGION = _spots_columns[7]["name"]
    QUALITY = _spots_columns[8]["name"]
    RADIUS = _spots_columns[9]["name"]
    FIELD_OF_VIEW = _spots_columns[10]["name"]
    ROUND = _ROUND


###################################################################################################
# Matrix

with open(directory / "schema/matrix/matrix_axes.json", "rb") as f:
    _matrix_axes = json.load(f)

with open(directory / "schema/matrix/matrix_features.json", "rb") as f:
    _matrix_features = json.load(f)

with open(directory / "schema/matrix/matrix_regions.json", "rb") as f:
    _matrix_regions = json.load(f)

MATRIX_CHUNK_SIZE = (5000, 1000)

MATRIX_NAME = "matrix"


class MATRIX_REQUIRED_REGIONS(str, Enum):
    REGION_ID = _matrix_regions[0]["name"]
    X_REGION = _matrix_regions[1]["name"]
    Y_REGION = _matrix_regions[2]["name"]


class MATRIX_OPTIONAL_REGIONS(str, Enum):
    Z_REGION = _matrix_regions[3]["name"]
    PHYS_ANNOTATION = _matrix_regions[4]["name"]
    TYPE_ANNOTATION = _matrix_regions[5]["name"]
    GROUP_ID = _matrix_regions[6]["name"]
    FIELD_OF_VIEW = _matrix_regions[7]["name"]
    AREA_PIXELS = _matrix_regions[8]["name"]
    AREA_UM2 = _matrix_regions[9]["name"]


class MATRIX_AXES(str, Enum):
    REGIONS = _matrix_axes[0]["name"]
    FEATURES = _matrix_axes[1]["name"]


class MATRIX_REQUIRED_FEATURES(str, Enum):
    GENE_NAME = _matrix_features[0]["name"]


class MATRIX_OPTIONAL_FEATURES(str, Enum):
    ROUND = _ROUND
    CHANNEL = _CHANNEL

class SCANPY_CONSTANTS:
    SPATIAL_LAYOUT = "X_spatial"

###################################################################################################
# Regions

with open(directory / "schema/regions/regions_axes.json", "rb") as f:
    _regions_axes = json.load(f)

REGIONS_NAME = "regions"


class REGIONS_AXES(str, Enum):
    Y_REGION = _regions_axes[0]["name"]
    X_REGION = _regions_axes[1]["name"]
