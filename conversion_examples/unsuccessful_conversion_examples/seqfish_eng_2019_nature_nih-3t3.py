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
from collections import defaultdict
from math import floor
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
    REQUIRED_ATTRIBUTES.ASSAY: ASSAYS.SEQFISH,
    REQUIRED_ATTRIBUTES.AUTHORS:
        "Chee-Huat Linus eng, Michael Lawson, Qian Zhu, Ruben Dries, Noushin Koulena, Yodai "
        "takei, Jina Yun, Christopher Cronin, Christoph Karp, Guo-Cheng Yuan & Long Cai",
    REQUIRED_ATTRIBUTES.YEAR: 2019,
    OPTIONAL_ATTRIBUTES.PUBLICATION_NAME:
        "Transcriptome-scale super-resolved imaging in tissues by RNA seqFISH+",
    OPTIONAL_ATTRIBUTES.PUBLICATION_URL: "https://doi.org/10.1038/s41586-019-1049-y",
    OPTIONAL_ATTRIBUTES.NOTES:
        "pixel locations are local, not global. Spots must be plotted by field of view"
}

dirpath = Path(os.path.expanduser(
    "~/google_drive/czi/spatial-approaches/in-situ-transcriptomics/seqfish/seqfish-plus/sourcedata/"
))

centroids_file = dirpath / "cortex_svz_cellcentroids.csv"
centroids = pd.read_csv(centroids_file)

gene_names_file = dirpath.parent / "all_gene_Names.mat"
gene_names = pd.Series(np.array(
    [v[0] for v in scipy.io.loadmat(gene_names_file)["allNames"]], dtype="U"
).reshape(-1))

spots_path = dirpath / "RNA_locations_cell_cortex/"
spots_files = spots_path.glob("*.csv")

spot_data = defaultdict(list)

NON_UNIQUE_CELL_ID = "non_unique_cell_id"
SEQFISH_NUMERIC_GENE_ID = "seqfish_numeric_gene_id"

for f in spots_files:
    *_, cell_number = f.stem.split("_")

    # cell id is not unique, it depends on fov
    try:
        int_cell = int(cell_number)
        fov = int(centroids.loc[int_cell, "Field of View"])
        x_region = centroids.loc[int_cell, "X"]
        y_region = centroids.loc[int_cell, "Y"]
    except KeyError:
        continue  # cell not found in centroids

    raw_data = pd.read_csv(f)
    spot_data[SPOTS_REQUIRED_VARIABLES.X_SPOT].extend(np.asarray(raw_data.iloc[0, :]))
    spot_data[SPOTS_REQUIRED_VARIABLES.Y_SPOT].extend(np.asarray(raw_data.iloc[1, :]))
    spot_data[SEQFISH_NUMERIC_GENE_ID].extend(
        np.array(list(map(lambda x: floor(float(x)), raw_data.columns)), dtype=int)
    )
    spot_data[SPOTS_OPTIONAL_VARIABLES.FIELD_OF_VIEW].extend([fov] * raw_data.shape[1])
    spot_data[NON_UNIQUE_CELL_ID].extend([cell_number] * raw_data.shape[1])
    spot_data[SPOTS_OPTIONAL_VARIABLES.X_REGION].extend([x_region] * raw_data.shape[1])
    spot_data[SPOTS_OPTIONAL_VARIABLES.Y_REGION].extend([y_region] * raw_data.shape[1])

# define the gene_id
spot_data[SPOTS_REQUIRED_VARIABLES.GENE_NAME] = gene_names[spot_data[SEQFISH_NUMERIC_GENE_ID]]
del spot_data[SEQFISH_NUMERIC_GENE_ID]

# make a dataframe
spot_df = pd.DataFrame(spot_data)

# create a unique id for each cell
ids = spot_df.groupby([SPOTS_OPTIONAL_VARIABLES.FIELD_OF_VIEW, NON_UNIQUE_CELL_ID]).size()
ids.values[:] = np.arange(ids.shape[0])

indexer = pd.MultiIndex.from_frame(spot_df[[SPOTS_OPTIONAL_VARIABLES.FIELD_OF_VIEW, NON_UNIQUE_CELL_ID]])
unique_cell_ids = ids[indexer].values
spot_df[SPOTS_OPTIONAL_VARIABLES.REGION_ID] = unique_cell_ids
del spot_df[NON_UNIQUE_CELL_ID]

spots = starspace.Spots.from_spot_data(spot_df, attrs=attributes)
# x[0] y[1]; these are (2, num_spots) shaped arrays

# build spot data
# these data have per-fov pixel information for x, y. There is no global coordinate space.

# TODO incomplete, I wanted to get some proteomics data done.
matrix = spots.to_spatial_matrix()
