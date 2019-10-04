"""
Visualization and analysis of gene expression in tissue sections by spatial transcriptomics
===========================================================================================

Patrik L. Ståhl, Fredrik Salmén, Sanja Vickovic, Anna Lundmark, José Fernández Navarro, Jens Magnusson,
Stefania Giacomello, Michaela Asp, Jakub O. Westholm4, Mikael Huss4, Annelie Mollbrink2,
Sten Linnarsson, Simone Codeluppi, Åke Borg, Fredrik Pontén, Paul Igor Costea, Pelin Sahlén,
Jan Mulder, Olaf Bergmann, Joakim Lundeberg, Jonas Frisén

this publication can be found at https://science.sciencemag.org/content/353/6294/78.long and the
data referenced below can be downloaded from
https://www.spatialresearch.org/resources-published-datasets/doi-10-1126science-aaf2403/

checklist:
- [x] point locations
- [x] cell locations (NA)
- [x] cell x gene expression matrix (NA)

load the data
-------------
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import dask.array as da
from skimage.transform import matrix_transform

import starspace
from starspace.constants import *

dirpath = Path(os.path.expanduser(
    "~/google_drive/czi/spatial-approaches/spatial-transcriptomics/10.1126/science.aaf2403"
))

spots_file = dirpath / "Layer1_BC_count_matrix-1.tsv"
transformations_file = dirpath / "Layer1_BC_transformation.txt"
image_file = dirpath / "HE_layer1_BC.jpg"

attributes = {
    REQUIRED_ATTRIBUTES.AUTHORS: (
        "Patrik L. Ståhl", "Fredrik Salmén", "Sanja Vickovic", "Anna Lundmark",
        "José Fernández Navarro", "Jens Magnusson", "Stefania Giacomello", "Michaela Asp",
        "Jakub O. Westholm", "Mikael Huss", "Annelie Mollbrink", "Sten Linnarsson",
        "Simone Codeluppi", "Åke Borg", "Fredrik Pontén", "Paul Igor Costea", "Pelin Sahlén",
        "Jan Mulder", "Olaf Bergmann", "Joakim Lundeberg", "Jonas Frisén"
    ),
    REQUIRED_ATTRIBUTES.YEAR: 2016,
    REQUIRED_ATTRIBUTES.SAMPLE_TYPE: "prostate cancer",
    REQUIRED_ATTRIBUTES.ORGANISM: "human",
    REQUIRED_ATTRIBUTES.ASSAY: ASSAYS.SPATIAL_TRANSCRIPTOMICS.value,
    OPTIONAL_ATTRIBUTES.PUBLICATION_NAME: (
        "Visualization and analysis of gene expression in tissue sections by spatial "
        "transcriptomics"
    ),
    OPTIONAL_ATTRIBUTES.PUBLICATION_URL: "https://science.sciencemag.org/content/353/6294/78.long"
}
# convert the spots data
# cells maybe need a radius?
data = pd.read_csv(spots_file, sep='\t', index_col=0)

# transform coordinates
with open(transformations_file, 'r') as f:
    transform = np.array([float(v) for v in f.read().strip().split()]).reshape(3, 3).T

x, y = zip(*[map(float, v.split('x')) for v in data.index])

xy = np.hstack([
    np.array(x)[:, None],
    np.array(y)[:, None],
])

transformed = matrix_transform(xy, transform)

dims = (MATRIX_AXES.REGIONS.value, MATRIX_AXES.FEATURES.value)
coords = {
    MATRIX_REQUIRED_REGIONS.REGION_ID: (MATRIX_AXES.REGIONS, np.arange(data.shape[0])),
    MATRIX_REQUIRED_REGIONS.X_REGION: (MATRIX_AXES.REGIONS, transformed[:, 0]),
    MATRIX_REQUIRED_REGIONS.Y_REGION: (MATRIX_AXES.REGIONS, transformed[:, 1]),
    MATRIX_REQUIRED_FEATURES.GENE_NAME: (MATRIX_AXES.FEATURES, data.columns)
}
data = da.from_array(data.values, chunks=MATRIX_CHUNK_SIZE)

matrix = starspace.Matrix.from_expression_data(
    data=data, coords=coords, dims=dims, name="matrix", attrs=attributes
)
url = "spatial-transcriptomics-stahl-2016-science-prostate-cancer"
matrix.save_zarr(url=url)
