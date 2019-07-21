import enum

CHUNK_SIZE = (5000, 1000)


class AXES:
    REGIONS = "regions"
    FEATURES = "features"


class FEATURES:
    GENE_NAME = "gene_name"


class REGIONS:
    ID = "region_id"
    X = "x"
    Y = "y"
    Z = "z"
    ANNOTATION = "annotation"
    GROUP_ID = "group_id"


class ATTRIBUTES:
    ORGANISM = "organism"
    ASSAY = "assay"
    YEAR = "year"
    AUTHORS = "authors"
    PUBLICATION_NAME = "publication_name"


class ASSAYS(enum.Enum):
    MERFISH = "MERFISH"
