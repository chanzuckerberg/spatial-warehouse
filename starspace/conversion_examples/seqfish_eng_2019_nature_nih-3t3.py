"""
# title
============================================================================================

#authors

this publication can be found at https://www.nature.com/articles/s41592-018-0175-z and the
data referenced below can be downloaded from http://linnarssonlab.org/osmfish/

checklist:
- [x] point locations
- [x] cell locations
- [x] cell x gene expression matrix

load the data
-------------
"""

from pathlib import Path
import os

import pandas as pd

import starspace
from starspace.constants import *

dirpath = Path(os.path.expanduser(
    "~/google_drive/czi/spatial-approaches/in-situ-transcriptomics/seqfish/seqfish-plus/sourcedata/"
))

spots_path = dirpath / "RNA_locations_cell_cortex/"
spots_files = spots_path.glob("*.csv")

spot_data = {f: pd.read_csv(f) for f in spots_files}

centroids_file = dirpath / "cortex_svz_cellcentroids.csv"
centroids = pd.read_csv(centroids_file)

# x[0] y[1]; these are (2, num_spots) shaped arrays

# build spot data
# these data have per-fov pixel information for x, y. There is no global coordinate space.

# TODO incomplete, I wanted to get some proteomics data done.

