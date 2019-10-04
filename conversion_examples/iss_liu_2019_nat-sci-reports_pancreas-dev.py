"""
Modeling Spatial Correlation of Transcripts with Application to Developing Pancreas
===================================================================================

Ruishan Liu, Marco Mignardi, Robert Jones, Martin Enge, Seung K. Kim, Stephen R. Quake & James Zou

This publication can be found at https://www.nature.com/articles/s41598-019-41951-2 and the data
can be downloaded from https://cirm.ucsc.edu/projects

Checklist:
- [x] point locations
- [~] cell locations  (centroids only)
- [x] cell x gene expression matrix (derivable)

"""
import requests
from pathlib import Path
from io import BytesIO

import pandas as pd

import starspace
from starspace.constants import *

response = requests.get(
    "https://d24h2xsgaj29mf.cloudfront.net/raw/iss_liu_2019_nat-sci-reports_pancreas-dev/"
    "Nuc_TOT_2p2.txt"
)
region_data = pd.read_csv(BytesIO(response.content))

response = requests.get(
    "https://d24h2xsgaj29mf.cloudfront.net/raw/iss_liu_2019_nat-sci-reports_pancreas-dev/"
    "RNA_TOT_2p2.txt"
)
rna_data = pd.read_csv(BytesIO(response.content))

response = requests.get(
    "https://d24h2xsgaj29mf.cloudfront.net/raw/iss_liu_2019_nat-sci-reports_pancreas-dev/"
    "Conversion_Pool2.txt"
)
gene_map = pd.read_csv(BytesIO(response.content))

##################################################################################################
# Build the spot table


# some of these spots don't map to real genes. Interesting. Definitely retain "Barcode_Num" and
# "Barcode_Letter"
gene_map = gene_map.set_index("Barcode_Num")
gene_info = gene_map.loc[rna_data.Seq_num, :]
gene_info.index = rna_data.index

rna_data = pd.concat([rna_data, gene_info], axis=1)

# "ObjectNumber" is the join key for gene ids, but we've joined all the tables, so we can drop it.
rna_data = rna_data.drop("ObjectNumber", axis=1)

# merge in cell centroids
region_data = region_data.set_index("ObjectNumber")
region_data = region_data.drop("ImageNumber", axis=1)  # duplicated in rna_data
region_info = region_data.loc[rna_data["Parent_Cells"], :]
region_info.index = rna_data.index

rna_data = pd.concat([rna_data, region_info], axis=1)

notes = list()
notes.append("'seq_num' contains channel information for the in-situ sequencing code of each gene")
notes.append("'barcode_letter' contains the nucleotides read out using ISS")


column_map = {
    "ImageNumber": SPOTS_OPTIONAL_VARIABLES.FIELD_OF_VIEW,
    "Blob_X": SPOTS_REQUIRED_VARIABLES.X_SPOT,
    "Blob_Y": SPOTS_REQUIRED_VARIABLES.Y_SPOT,
    "Parent_Cells": SPOTS_OPTIONAL_VARIABLES.REGION_ID,
    "Location_Center_X": SPOTS_OPTIONAL_VARIABLES.X_REGION,
    "Location_Center_Y": SPOTS_OPTIONAL_VARIABLES.Y_REGION,
    "Gene_Name": SPOTS_REQUIRED_VARIABLES.GENE_NAME,
    "Seq_qual": SPOTS_OPTIONAL_VARIABLES.QUALITY,
    "Seq_num": "seq_num",
    "Barcode_Letter": "barcode_letter",
}

columns = [column_map[c] for c in rna_data.columns]
rna_data.columns = columns

attributes = {
    REQUIRED_ATTRIBUTES.ASSAY: ASSAYS.ISS.value,
    REQUIRED_ATTRIBUTES.SAMPLE_TYPE: "fetal pancreas",
    REQUIRED_ATTRIBUTES.AUTHORS: [
        "Ruishan Liu", "Marco Mignardi", "Robert Jones", "Martin Enge", "Seung K. Kim", "Stephen R. Quake" "James Zou"
    ],
    REQUIRED_ATTRIBUTES.YEAR: 2019,
    REQUIRED_ATTRIBUTES.ORGANISM: "human",
    OPTIONAL_ATTRIBUTES.PUBLICATION_NAME: (
        "Modeling Spatial Correlation of Transcripts with Application to Developing Pancreas"
    ),
    OPTIONAL_ATTRIBUTES.PUBLICATION_URL: "https://www.nature.com/articles/s41598-019-41951-2"
}

spots = starspace.Spots.from_spot_data(rna_data, attributes)


# s3_url = "s3://starfish.data.output-warehouse/iss_liu_2019_nat-sci-reports_pancreas-dev/"
url = "iss_liu_2019_nat-sci-reports_pancreas-dev/"
spots.save_zarr(url=url)


##################################################################################################
# we have the needed information to pivot into a matrix, too

matrix = spots.to_spatial_matrix()
matrix.save_zarr(url=url)
