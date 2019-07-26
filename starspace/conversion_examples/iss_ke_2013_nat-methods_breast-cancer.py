"""

============================================================================================

Rongqin Ke, Marco Mignardi, Alexandra Pacureanu, Jessica Svedlund, Johan Botling, Carolina Wählby,
Mats Nilsson

This publication can be found at https://science.sciencemag.org/content/348/6233/aaa6090 and the
data referenced below can be downloaded from

Checklist:
- [x] point locations
- [ ] cell locations
- [ ] cell x gene expression matrix (derivable)

Load the data
-------------
"""
from pathlib import Path

import pandas as pd
import xarray as xr

from starspace._constants import SPOTS_REQUIRED_VARIABLES, SPOTS_OPTIONAL_VARIABLES, \
    REQUIRED_ATTRIBUTES, ASSAYS, OPTIONAL_ATTRIBUTES, SPOTS_DIMS
from starspace import SpatialDataTypes


dirpath = Path("~/google_drive/czi/spatial-approaches/in-situ-transcriptomics/ISS/2013_mignardi_breast")

counts = dirpath / "all_spots.csv"

data = pd.read_csv(counts)

column_map = {
    "gene": SPOTS_REQUIRED_VARIABLES.GENE_NAME.value,
    "x": SPOTS_REQUIRED_VARIABLES.X_SPOT.value,
    "y": SPOTS_REQUIRED_VARIABLES.Y_SPOT.value,
    "qual": SPOTS_OPTIONAL_VARIABLES.QUALITY.value,
    "fov": SPOTS_OPTIONAL_VARIABLES.FIELD_OF_VIEW.value,
    "gene_code": "gene_code",
    "barcode": "barcode",
}

authors = [
    "Rongqin Ke", "Marco Mignardi", "Alexandra Pacureanu", "Jessica Svedlund", "Johan Botling", "Carolina Wählby",
    "Mats Nilsson"
]
attributes = {
    REQUIRED_ATTRIBUTES.ASSAY: ASSAYS.ISS,
    REQUIRED_ATTRIBUTES.SAMPLE_TYPE: "Her2+ breast carcinoma",
    REQUIRED_ATTRIBUTES.AUTHORS: authors,
    REQUIRED_ATTRIBUTES.YEAR: 2013,
    REQUIRED_ATTRIBUTES.ORGANISM: "human",
    OPTIONAL_ATTRIBUTES.PUBLICATION_NAME: "In situ sequencing for RNA analysis in preserved tissue and cells",
    OPTIONAL_ATTRIBUTES.PUBLICATION_URL: "https://www.nature.com/articles/nmeth.2563",
}

standard_columns = [column_map[c] for c in data.columns]

data.columns = standard_columns
data.index.name = SPOTS_DIMS.SPOTS

dataset = xr.Dataset.from_dataframe(data)
dataset.attrs = attributes

SpatialDataTypes.SPOTS.write(dataset, "s3://starfish.data.output-warehouse/iss_ke_2013_nat-methods_breast-cancer")

######################################################################################################################
# load the second dataset

counts2 = dirpath / "all_spots_2.csv"

data2 = pd.read_csv(counts2)
standard_columns = [column_map[c] for c in data2.columns]

data2.columns = standard_columns
data2.index.name = SPOTS_DIMS.SPOTS

dataset2 = xr.Dataset.from_dataframe(data2)
dataset2.attrs = attributes

# I'm not sure how this is different, so going to leave this.

######################################################################################################################
# load the gene_counts.csv

gene_counts = dirpath / "gene_cnts.csv"

gene_data = pd.read_csv(gene_counts)

# ok, just a summary file; can abandon this as it's derivable from the initial file.
