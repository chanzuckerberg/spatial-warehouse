"""
Spatially resolved, highly multiplexed RNA profiling in single cells
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
import requests
from io import BytesIO

import pandas as pd

import starspace
from starspace.constants import *

response = requests.get(
    "https://d24h2xsgaj29mf.cloudfront.net/raw/iss_ke_2013_nat-methods_breast-cancer/all_spots.csv"
)

data = pd.read_csv(BytesIO(response.content))

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
    "Rongqin Ke", "Marco Mignardi", "Alexandra Pacureanu", "Jessica Svedlund", "Johan Botling",
    "Carolina Wählby", "Mats Nilsson"
]
attributes = {
    REQUIRED_ATTRIBUTES.ASSAY: ASSAYS.ISS,
    REQUIRED_ATTRIBUTES.SAMPLE_TYPE: "Her2+ breast carcinoma",
    REQUIRED_ATTRIBUTES.AUTHORS: authors,
    REQUIRED_ATTRIBUTES.YEAR: 2013,
    REQUIRED_ATTRIBUTES.ORGANISM: "human",
    OPTIONAL_ATTRIBUTES.PUBLICATION_NAME: (
        "In situ sequencing for RNA analysis in preserved tissue and cells"
    ),
    OPTIONAL_ATTRIBUTES.PUBLICATION_URL: "https://www.nature.com/articles/nmeth.2563",
}

standard_columns = [column_map[c] for c in data.columns]
data.columns = standard_columns

spots = starspace.Spots.from_spot_data(data, attributes)

# s3_url = "s3://starfish.data.output-warehouse/iss_ke_2013_nat-methods_breast-cancer"
local_url = "iss_ke_2013_nat-methods_breast-cancer/"
spots.save_zarr(local_url)
