import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from .constants import SPOTS_REQUIRED_VARIABLES


def plot_spots(spots: xr.Dataset):
    f, ax = plt.subplots(dpi=150)
    genes = np.unique(spots[SPOTS_REQUIRED_VARIABLES.GENE_NAME])
    gene_map = dict(zip(genes, np.arange(genes.shape[0])))
    colors = [gene_map[v] for v in np.asarray(spots[SPOTS_REQUIRED_VARIABLES.GENE_NAME])]
    ax.scatter(
        spots[SPOTS_REQUIRED_VARIABLES.X_SPOT],
        spots[SPOTS_REQUIRED_VARIABLES.Y_SPOT],
        c=colors,
        cmap=plt.cm.nipy_spectral,
        s=4,
        alpha=0.4,
    )
    return f


def plot_cells():
    """do a small gut check that the data is worth something."""
    raise NotImplementedError
