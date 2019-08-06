"""
Transcriptome-scale super-resolved imaging in tissues by RNA seqFISH+
============================================================================================
Chee-Huat Linus eng, Michael Lawson, Qian Zhu, Ruben Dries, Noushin Koulena, Yodai takei, Jina Yun,
Christopher Cronin, Christoph Karp, Guo-Cheng Yuan & Long Cai

this publication can be found at https://doi.org/10.1038/s41586-019-1049-y and the
data referenced below can be downloaded from http://doi.org/10.5281/zenodo.2669683

checklist:
- [x] point locations
- [x] cell locations
- [x] cell x gene expression matrix

load the data
-------------
"""

from pathlib import Path
import os

import numpy as np
import pandas as pd
import scipy.io

import starspace
from starspace.constants import *

attributes = {
    REQUIRED_ATTRIBUTES.ORGANISM: "mouse",
    REQUIRED_ATTRIBUTES.SAMPLE_TYPE: "brain",
    REQUIRED_ATTRIBUTES.AUTHORS:
        "Chee-Huat Linus eng, Michael Lawson, Qian Zhu, Ruben Dries, Noushin Koulena, Yodai "
        "takei, Jina Yun, Christopher Cronin, Christoph Karp, Guo-Cheng Yuan & Long Cai",
    REQUIRED_ATTRIBUTES.YEAR: 2019,
    OPTIONAL_ATTRIBUTES.PUBLICATION_NAME:
        "Transcriptome-scale super-resolved imaging in tissues by RNA seqFISH+",
    OPTIONAL_ATTRIBUTES.PUBLICATION_URL: "https://doi.org/10.1038/s41586-019-1049-y",
}

dirpath = Path(os.path.expanduser(
    "~/google_drive/czi/spatial-approaches/in-situ-transcriptomics/seqfish/seqfish-plus/sourcedata/"
))

spots_path = dirpath / "RNA_locations_cell_cortex/"
spots_files = spots_path.glob("*.csv")

centroids_file = dirpath / "cortex_svz_cellcentroids.csv"
centroids = pd.read_csv(centroids_file)

gene_names_file = dirpath.parent / "all_gene_Names.mat"
gene_names = np.ravel(scipy.io.loadmat(gene_names_file)["allNames"])

spot_data = {
    SPOTS_REQUIRED_VARIABLES.X_SPOT: [],
    SPOTS_REQUIRED_VARIABLES.Y_SPOT: [],
    SPOTS_REQUIRED_VARIABLES.GENE_NAME: [],
    SPOTS_OPTIONAL_VARIABLES.FIELD_OF_VIEW: [],
    SPOTS_OPTIONAL_VARIABLES.REGION_ID: [],
}
for f in spots_files:
    *_, cell_number = f.stem.split("_")

    # cell id is not unique, it depends on fov
    fov = int(centroids.loc[cell_number, "Field of View"])

    raw_data = pd.read_csv(f)
    spot_data[SPOTS_REQUIRED_VARIABLES.X_SPOT].extend(np.asarray(raw_data[0, :]))
    spot_data[SPOTS_REQUIRED_VARIABLES.Y_SPOT].extend(np.asarray(raw_data[1, :]))
    spot_data[SPOTS_REQUIRED_VARIABLES.GENE_NAME].extend(np.floor([int(v) for v in raw_data.index]))
    spot_data[SPOTS_OPTIONAL_VARIABLES.FIELD_OF_VIEW].extend([fov] * raw_data.shape[1])
    spot_data[SPOTS_OPTIONAL_VARIABLES.REGION_ID].extend([cell_number] * raw_data.shape[1])

starspace.Spots.from_spot_data(pd.DataFrame(spot_data), attrs=attributes)

# x[0] y[1]; these are (2, num_spots) shaped arrays

# build spot data
# these data have per-fov pixel information for x, y. There is no global coordinate space.

# TODO incomplete, I wanted to get some proteomics data done.

