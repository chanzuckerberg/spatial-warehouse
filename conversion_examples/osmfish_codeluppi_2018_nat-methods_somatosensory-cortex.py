"""
spatial organization of the somatosensory cortex revealed by cyclic smfish
============================================================================================

simone codeluppi, lars e. borm, amit zeisel, gioele la manno, josina a. van lunteren,
camilla i. svensson, sten linnarsson

this publication can be found at https://www.nature.com/articles/s41592-018-0175-z and the
data referenced below can be downloaded from http://linnarssonlab.org/osmfish/

checklist:
- [x] point locations
- [x] cell locations
- [x] cell x gene expression matrix

load the data
-------------
"""

import pickle
import re
import requests
from itertools import repeat
from io import BytesIO
import tempfile

import dask.array as da
import h5py
import loompy
import numpy as np
import pandas as pd

import starspace
from starspace.constants import *

response = requests.get(
    "https://d24h2xsgaj29mf.cloudfront.net/raw/"
    "osmfish_codeluppi_2018_nat-methods_somatosensory-cortex/"
    "mRNA_coords_raw_counting.hdf5"
)
spots_data = h5py.File(BytesIO(response.content), "r")

response = requests.get(
    "https://d24h2xsgaj29mf.cloudfront.net/raw/"
    "osmfish_codeluppi_2018_nat-methods_somatosensory-cortex/"
    "polyT_seg.pkl"
)
region_data = pickle.load(BytesIO(response.content))



# load spot info
gene = []
x = []
y = []
imaging_round = []
pattern = r"^(.*?)_Hybridization(\d*?)$"
for k in spots_data.keys():
    gene_, round_ = re.match(pattern, k).groups()
    gene_data = spots_data[k]
    x.extend(gene_data[:, 0])
    y.extend(gene_data[:, 1])
    gene.extend(repeat(gene_, gene_data.shape[0]))
    imaging_round.extend(repeat(int(round_), gene_data.shape[0]))

spots_data.close()

# build the spot information
spot_data = pd.DataFrame({
    SPOTS_REQUIRED_VARIABLES.GENE_NAME: gene,
    SPOTS_REQUIRED_VARIABLES.X_SPOT: x,
    SPOTS_REQUIRED_VARIABLES.Y_SPOT: y,
    SPOTS_OPTIONAL_VARIABLES.ROUND: imaging_round,
})

# construct the attributes
attributes = {
    REQUIRED_ATTRIBUTES.AUTHORS: (
        "Simone Codeluppi", "Lars E. Borm", "Amit Zeisel", "Gioele La Manno",
        "Josina A. van Lunteren", "Camilla I. Svensson", "Sten Linnarsson"
    ),
    REQUIRED_ATTRIBUTES.YEAR: 2018,
    REQUIRED_ATTRIBUTES.SAMPLE_TYPE: "somatosensory cortex",
    REQUIRED_ATTRIBUTES.ORGANISM: "mouse",
    REQUIRED_ATTRIBUTES.ASSAY: ASSAYS.OSMFISH.value,
    OPTIONAL_ATTRIBUTES.PUBLICATION_NAME: (
        "Spatial organization of the somatosensory cortex revealed by cyclic smFISH"
    ),
    OPTIONAL_ATTRIBUTES.PUBLICATION_URL: "https://www.nature.com/articles/s41592-018-0175-z"
}

spots = starspace.Spots.from_spot_data(spot_data, attrs=attributes)
s3_url = (
    "s3://starfish.data.output-warehouse/osmfish-codeluppi-2018-nat-methods-somatosensory-cortex/"
)
url = "osmfish-codeluppi-2018-nat-methods-somatosensory-cortex/"
spots.save_zarr(url=url)

###################################################################################################
# load the region information; we're gonna be lazy and just create a label image. Makes for simple
# lookups. It's only 6 gb, and we can put it in dask, so w/e
# find the extent of the images from the spots and the region data

x_min, x_max = np.percentile(spot_data[SPOTS_REQUIRED_VARIABLES.X_SPOT], [0, 100])
y_min, y_max = np.percentile(spot_data[SPOTS_REQUIRED_VARIABLES.Y_SPOT], [0, 100])

label = np.empty((int(x_max) + 1, int(y_max) + 1), dtype=np.int16)

for region_id, array in region_data.items():
    region_id = int(region_id)
    x = array[:, 0]
    y = array[:, 1]
    label[x, y] = region_id

dims = tuple(REGIONS_AXES)

regions = starspace.Regions.from_label_image(label, dims=dims, attrs=attributes)
regions.save_zarr(url=url)

###################################################################################################
# load up the count matrix

response = requests.get(
    "https://d24h2xsgaj29mf.cloudfront.net/raw/"
    "osmfish_codeluppi_2018_nat-methods_somatosensory-cortex/"
    "osmFISH_SScortex_mouse_all_cells.loom"
)
with tempfile.TemporaryDirectory() as tmpdirname:
    with open(os.path.join(tmpdirname, "temp.loom"), 'wb') as f:
        f.write(response.content)
    conn = loompy.connect(os.path.join(tmpdirname, "temp.loom"), mode="r")

    row_attrs = dict(conn.row_attrs)
    col_attrs = dict(conn.col_attrs)

    data = da.from_array(conn[:, :].T, chunks=MATRIX_CHUNK_SIZE)

# region id should be int dtype
col_attrs["CellID"] = col_attrs["CellID"].astype(int)

dims = (MATRIX_AXES.REGIONS.value, MATRIX_AXES.FEATURES.value)

coords = {
    MATRIX_REQUIRED_REGIONS.REGION_ID: (MATRIX_AXES.REGIONS, col_attrs["CellID"]),
    MATRIX_REQUIRED_REGIONS.X_REGION: (MATRIX_AXES.REGIONS, col_attrs["X"]),
    MATRIX_REQUIRED_REGIONS.Y_REGION: (MATRIX_AXES.REGIONS, col_attrs["Y"]),
    MATRIX_OPTIONAL_REGIONS.GROUP_ID: (MATRIX_AXES.REGIONS, col_attrs["ClusterID"]),
    MATRIX_OPTIONAL_REGIONS.TYPE_ANNOTATION: (MATRIX_AXES.REGIONS, col_attrs["ClusterName"]),
    MATRIX_OPTIONAL_REGIONS.PHYS_ANNOTATION: (MATRIX_AXES.REGIONS, col_attrs["Region"]),
    MATRIX_OPTIONAL_REGIONS.AREA_PIXELS: (MATRIX_AXES.REGIONS, col_attrs["size_pix"]),
    MATRIX_OPTIONAL_REGIONS.AREA_UM2: (MATRIX_AXES.REGIONS, col_attrs["size_um2"]),
    "valid": (MATRIX_AXES.REGIONS, col_attrs["Valid"]),
    "tsne_1": (MATRIX_AXES.REGIONS, col_attrs["_tSNE_1"]),
    "tsne_2": (MATRIX_AXES.REGIONS, col_attrs["_tSNE_2"]),
    MATRIX_OPTIONAL_FEATURES.CHANNEL: (MATRIX_AXES.FEATURES, row_attrs["Fluorophore"]),
    MATRIX_REQUIRED_FEATURES.GENE_NAME: (MATRIX_AXES.FEATURES, row_attrs["Gene"]),
    MATRIX_OPTIONAL_FEATURES.ROUND.value: (MATRIX_AXES.FEATURES, row_attrs["Hybridization"]),
}

matrix = starspace.Matrix.from_expression_data(
    data=data, coords=coords, dims=dims, name="matrix", attrs=attributes
)
matrix.save_zarr(url=url)

