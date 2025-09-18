"""
written by ddesarn
Exercise of loading in medical imgs - complete load_3d_imgs_demo

Objective: load in the 3D volume found in the simulated CT data and return the images as a 3D numpy array
"""

import os
import numpy as np
import pydicom as pyd
import glob
import matplotlib.pyplot as plt
from file_io.imio import *


def plot_imgs(imgs: np.ndarray):
    """
    Helper function that takes a 3D or 4D numpy array as input and plots out the slices (and timepoints if 4D)
    cmap is the color map, 'grey' give a grayscale looking color mapping
    vmin is the minimum window value (values below will be set at the lower color)
    vmax is the maximum window value (values above will be set at the upper color
    """
    # Plotting 3D data or 4D data
    if (imgs.ndim == 3) or (imgs.ndim == 4 and imgs.shape[-1] == 1):
        for slc in range(len(imgs)):
            plt.imshow(imgs[slc], cmap='grey', vmin=-100, vmax=100)
            plt.title(f'slc {slc}')
            plt.colorbar()
            plt.show()
            plt.close()
    else:
        for slc in range(len(imgs)):
            for tp in range(imgs.shape[-1]):
                plt.imshow(imgs[slc, :, :, tp], vmin=1E-8, vmax=2500)
                plt.title(f'slc {slc}, tp {tp}')
                plt.colorbar()
                plt.show()
                plt.close()
    return


def load_3d_imgs_demo(ddir):
    """
    Given the directory of data containing the DICOM files, loads the images
    """

    return # imgs


# Automatic path finding of the data
os.chdir('..')
test_files_dir = rf'{os.getcwd()}\test_files'
data_dir_3d = rf'{test_files_dir}\simulated_CT_data'  # 3D data

# TODO! finish this function that loads the 3D images - you can use the plot_imgs to plot the returned images when done
imgs = load_3d_imgs_demo(data_dir_3d)
# plot_imgs(imgs)  # Uncomment if you want to plot your images!


# # # Uncomment to load in the 4D images - it is a lot more work to include time! Use file_io.imio functions to do this
# data_dir_4d = rf"{test_files_dir}\simulated_PET_data"     # 4D data
# imgs = load_dcm_imgs(data_dir_4d)
# plot_imgs(imgs)


