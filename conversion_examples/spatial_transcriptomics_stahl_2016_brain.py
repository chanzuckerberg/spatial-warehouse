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

from io import BytesIO

import dask.array as da
import numpy as np
import pandas as pd
import requests
from skimage.transform import matrix_transform

import starspace
from starspace.constants import *

response = requests.get(
    "https://d24h2xsgaj29mf.cloudfront.net/raw/spatial_transcriptomics_stahl_2016/"
    "Rep1_MOB_count_matrix-1.tsv"
)
data = pd.read_csv(BytesIO(response.content), sep='\t', index_col=0)

attributes = {
    REQUIRED_ATTRIBUTES.AUTHORS: (
        "Patrik L. Ståhl", "Fredrik Salmén", "Sanja Vickovic", "Anna Lundmark",
        "José Fernández Navarro", "Jens Magnusson", "Stefania Giacomello", "Michaela Asp",
        "Jakub O. Westholm", "Mikael Huss", "Annelie Mollbrink", "Sten Linnarsson",
        "Simone Codeluppi", "Åke Borg", "Fredrik Pontén", "Paul Igor Costea", "Pelin Sahlén",
        "Jan Mulder", "Olaf Bergmann", "Joakim Lundeberg", "Jonas Frisén"
    ),
    REQUIRED_ATTRIBUTES.YEAR: 2016,
    REQUIRED_ATTRIBUTES.SAMPLE_TYPE: "Olfactory Bulb",
    REQUIRED_ATTRIBUTES.ORGANISM: "mouse",
    REQUIRED_ATTRIBUTES.ASSAY: ASSAYS.SPATIAL_TRANSCRIPTOMICS.value,
    OPTIONAL_ATTRIBUTES.PUBLICATION_NAME: (
        "Visualization and analysis of gene expression in tissue sections by spatial "
        "transcriptomics"
    ),
    OPTIONAL_ATTRIBUTES.PUBLICATION_URL: "https://science.sciencemag.org/content/353/6294/78.long"
}
# convert the spots data
# cells maybe need a radius?

# transform coordinates
response = requests.get(
    "https://d24h2xsgaj29mf.cloudfront.net/raw/spatial_transcriptomics_stahl_2016/"
    "Rep1_MOB_transformation.txt"
)
transform = np.array([float(v) for v in response.content.decode().strip().split()]).reshape(3, 3).T

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
url = "spatial-transcriptomics-stahl-2016-science-olfactory-bulb"
matrix.save_zarr(url=url)
