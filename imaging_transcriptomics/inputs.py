from pathlib import Path

import nibabel as nib
import numpy as np
import pandas as pd
from scipy.stats import zscore

from .errors import (check_correct_shape,
                     check_path_exists,
                     check_extensions,
                     check_var_in_range)


# Imaging data
#@check_path_exists
#@check_extensions
def read_scan(path):
    """Return the imaging file associated to the input scan.

    Uses the `Nibabel <https://nipy.org/nibabel/>`_ to read the input imaging file and get the voxel data.

    :param str path: path of the imaging file to analyze.

    :return: Numpy matrix with the voxel of the input scan.
    """
    data = nib.load(Path(path)).get_fdata()
    return data


@check_correct_shape
def extract_average(imaging_matrix):
    """Extract the average value of the ROIs from the imaging scan.

    The values are extracted from the left hemisphere only, since the data of the Allen Human Brain Atlas are
    available for that hemisphere only for all donors.

    :param imaging_matrix: matrix with the voxels of the image.

    :return: numpy array with the average value from 41 brain regions.
    """
    n_regions = 41
    atlas_data = nib.load(Path(__file__).resolve().parent.parent / "data" /
                          "atlas-desikankilliany_1mm_MNI152.nii.gz").get_fdata()
    data = np.zeros(n_regions)
    for i in range(1, n_regions + 1):
        data[i - 1] = np.mean(imaging_matrix[np.where(atlas_data == i)])
    return np.array(data)


# Other parameters
@check_var_in_range
def get_components(target_variance, explained_var):
    """Return the optimal number of PLS components to explain a desired amount of the total variance.

    :param float target_variance: total explained variance
    :param np.array explained_var: array with explained variance by each individual pls component.

    :return int dim: optimal number of components to extract the desired explained variance.
    """
    dim = 1
    cumulative_var = np.cumsum(explained_var)
    while cumulative_var[dim-1] < target_variance:
        dim += 1
    return dim


# Gene expression data
def load_gene_expression():
    """Return matrix with gene expression data.

    The data have been previously normalised and are available in the  ``data`` sub-folder.

    :return: numpy array with the gene expression data.
    """
    expression_file_path = Path(__file__).resolve().parent.parent / "data" / "gene_expression_data.csv"
    expression_data = pd.read_csv(expression_file_path, sep=',')
    my_data_x = expression_data.iloc[0:41, 2:].to_numpy()
    return zscore(my_data_x, ddof=1)


def load_gene_labels():
    """Return an array with the gene labels.
    The gene labels are available in the ``data`` sub-folder.

    :return: numpy array with the labels of the genes.
    """
    genes_labels_path = Path(__file__).resolve().parent.parent / "data" / "gene_expression_labels.txt"
    return pd.read_fwf(genes_labels_path, header=None).to_numpy()