"""
Spatial organization of the somatosensory cortex revealed by cyclic smFISH
============================================================================================

Simone Codeluppi, Lars E. Borm, Amit Zeisel, Gioele La Manno, Josina A. van Lunteren,
Camilla I. Svensson, Sten Linnarsson

This publication can be found at https://www.nature.com/articles/s41592-018-0175-z and the
data referenced below can be downloaded from http://linnarssonlab.org/osmFISH/

Checklist:
- [x] point locations
- [x] cell locations
- [x] cell x gene expression matrix

Load the data
-------------
"""

import os
import pickle
import re
from itertools import repeat
from pathlib import Path

import dask.array as da
import h5py
import pandas as pd
import numpy as np

import starspace
from starspace._constants import REQUIRED_ATTRIBUTES, SPOTS_REQUIRED_VARIABLES, \
    SPOTS_OPTIONAL_VARIABLES, ASSAYS, OPTIONAL_ATTRIBUTES

dirpath = Path(os.path.expanduser(
    "~/google_drive/czi/spatial-approaches/in-situ-transcriptomics/osmFISH"
))

spots_file = dirpath / "mRNA_coords_raw_counting.hdf5"
cells_file = dirpath / "osmFISH_SScortex_mouse_all_cells.loom"
regions_file = dirpath / "polyT_seg.pkl"
incl_cells_file = dirpath / "Included_cells.p"

spots_data = h5py.File(spots_file, "r")

# load spot info
gene = []
x = []
y = []
round = []
pattern = r"^(.*?)_Hybridization(\d*?)$"
for k in spots_data.keys():
    gene_, round_ = re.match(pattern, k).groups()
    gene_data = spots_data[k]
    x.extend(gene_data[:, 0])
    y.extend(gene_data[:, 1])
    gene.extend(repeat(gene_, gene_data.shape[0]))
    round.extend(repeat(int(round_), gene_data.shape[0]))

spots_data.close()

# build the spot information
spots = pd.DataFrame({
    SPOTS_REQUIRED_VARIABLES.GENE_NAME: gene,
    SPOTS_REQUIRED_VARIABLES.X_SPOT: x,
    SPOTS_REQUIRED_VARIABLES.Y_SPOT: y,
    SPOTS_OPTIONAL_VARIABLES.ROUND: round,
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

dataset = starspace.converters.dataframe2annotated_spots(spots, attributes=attributes)

dataset = starspace.SpatialDataTypes.SPOTS.write(
    dataset,
    "s3://starfish.data.output-warehouse/osmfish-codeluppi-2018-nat-methods-somatosensory-cortex/",
)

###################################################################################################
# load the region information; we're gonna be lazy and just create a label image. Makes for simple
# lookups. It's only 6 gb, and we can put it in dask, so w/e

with open(regions_file, "rb") as f:
    region_data = pickle.load(f)

# find the extent of the images from the spots and the region data

x_min, x_max = np.percentile(spots[SPOTS_REQUIRED_VARIABLES.X_SPOT], [0, 100])
y_min, y_max = np.percentile(spots[SPOTS_REQUIRED_VARIABLES.Y_SPOT], [0, 100])

label = np.empty((int(x_max) + 1, int(y_max) + 1), dtype=np.int16)

for region_id, array in region_data.items():
    region_id = int(region_id)
    x = array[:, 0]
    y = array[:, 1]
    label[x, y] = region_id

# quick, make this massive thing a dask array!
dask_label_image = da.from_array(label, chunks=(1000, 1000))

dask_label_image.to_zarr()


