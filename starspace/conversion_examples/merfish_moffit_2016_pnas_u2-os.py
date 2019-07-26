"""
High-throughput single-cell gene-expression profiling with multiplexed error-robust fluorescence in situ hybridization
======================================================================================================================

Jeffrey R. Moffitt, Junjie Hao, Guiping Wang, Kok Hao Chen, Hazen P. Babcock, Xiaowei Zhuang

This publication can be found at https://www.pnas.org/content/113/39/11046 and the
data referenced below can be downloaded from
s3://starfish.data.published/MERFISH/20181005/starfish_results/benchmark_results.csv

Checklist:
- [x] point locations
- [ ] cell locations
- [ ] cell x gene expression matrix (derivable)

This file converts point locations constructed with a starfish pipeline that has 99.7%
correspondence to Jeff Moffit's original matlab processing of these same data. Minor deviations
are the result of numerical differences in deconvolution algorithms between matlab and python.

Load the data
-------------
"""

from pathlib import Path

import pandas as pd
import numpy as np

import starspace
from starspace._constants import ASSAYS, REQUIRED_ATTRIBUTES, OPTIONAL_ATTRIBUTES, SPOTS_REQUIRED_VARIABLES, \
    SPOTS_OPTIONAL_VARIABLES

data_path = Path("~/Downloads/") / "published_MERFISH_decoded_results.csv"

data = pd.read_csv(data_path, index_col=0)

# convert distance to quality; we'll map the name to quality below
data['distance'] = 1 - data['distance']

# drop the passes_thresholds column, this data has been conditioned on that previously
assert np.all(data['passes_thresholds'])
data = data.drop('passes_thresholds', axis=1)

# drop z_spot, it's not informative
assert np.allclose(data['zc'], 0.0005)
data = data.drop('zc', axis=1)

column_map = {
    'radius': SPOTS_OPTIONAL_VARIABLES.RADIUS.value,
    'target': SPOTS_REQUIRED_VARIABLES.GENE_NAME.value,
    'distance': SPOTS_OPTIONAL_VARIABLES.QUALITY.value,
    'xc': SPOTS_REQUIRED_VARIABLES.X_SPOT.value,
    'yc': SPOTS_REQUIRED_VARIABLES.Y_SPOT.value
}

columns = [column_map[c] for c in data.columns]
data.columns = columns
data.index.name = "spots"

attributes = {
    REQUIRED_ATTRIBUTES.ORGANISM: "human",
    REQUIRED_ATTRIBUTES.ASSAY: ASSAYS.MERFISH.value,
    REQUIRED_ATTRIBUTES.YEAR: 2016,
    REQUIRED_ATTRIBUTES.AUTHORS: [
        "Jeffrey R. Moffitt", "Junjie Hao", "Guiping Wang", "Kok Hao Chen", "Hazen P. Babcock",
        "Xiaowei Zhuang"
    ],
    REQUIRED_ATTRIBUTES.SAMPLE_TYPE: "osteosarcoma (bone, epithelial) cell line",
    OPTIONAL_ATTRIBUTES.PUBLICATION_NAME: (
        "High-throughput single-cell gene-expression profiling with multiplexed error-robust "
        "fluorescence in situ hybridization"
    ),
    OPTIONAL_ATTRIBUTES.PUBLICATION_URL: "https://www.pnas.org/content/113/39/11046"
}

dataset = starspace.converters.dataframe2annotated_spots(data, attributes)

starspace.SpatialDataTypes.SPOTS.write(
    dataset,
    url="s3://starfish.data.output-warehouse/merfish-moffit-2016-pnas-u2os/"
)

