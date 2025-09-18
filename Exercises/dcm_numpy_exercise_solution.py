"""
written by ddesarn
Exercise of loading in medical imgs - complete load_3d_imgs_demo

This solution also contains the things we went over in the recording
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

    fps = glob.glob(rf'{ddir}\*.dcm')
    imgs = []
    slc_locs = []
    for fp in fps:
        ds = pyd.dcmread(fp)
        # print(ds)
        img = ds.pixel_array
        rs = ds[0x28, 0x1053].value
        ri = ds[0x28, 0x1052].value
        img = img * rs + ri

        img_loc = ds.ImagePositionPatient   # Tuple, x, y, z location in mm at top left corner of image
        slc_loc = img_loc[-1]

        imgs.append(img)
        slc_locs.append(slc_loc)
    # print(len(imgs))
    # print(type(imgs[0]))
    # for slc_loc in slc_locs:
    #     print(slc_loc)

    # Sort the images!
    # [2, 1, 3], ['a', 'b', 'c'] = [[2, 'a'], [1, 'b'], [3, 'c']]
    combined = list(zip(slc_locs, imgs))
    combined_sorted = sorted(combined, key=lambda x: x[0])  # , reverse=True
    slc_locs_sorted, imgs_sorted = zip(*combined_sorted)

    # # Fun one liner !
    # slc_locs_sorted, imgs_sorted = zip(*sorted(zip(slc_locs, imgs), key=lambda x: x[0]))

    for ii in range(len(slc_locs)):
        print(slc_locs[ii])
        print(slc_locs_sorted[ii])

    imgs = np.array(imgs)
    return imgs


# Automatic path finding of the data
os.chdir('..')
test_files_dir = rf'{os.getcwd()}\test_files'
data_dir_3d = rf'{test_files_dir}\simulated_CT_data'  # 3D data

# TODO! this was the function to finish in the exercise
imgs = load_3d_imgs_demo(data_dir_3d)

# # Uncomment to load in the 4D images - it is a lot more work to include time! Use file_io.imio functions to do this
# data_dir_4d = rf"{test_files_dir}\simulated_PET_data"     # 4D data
# imgs, info = load_dcm_imgs(data_dir_4d, return_info=True)
# plot_imgs(imgs)


# NumPy
# Initialization
arr = np.array([0, 1, 2])
# print(arr)

arr = np.arange(10)
# print(arr)

arr = np.zeros((10, 10))
# print(arr)

arr = np.random.rand(5*5).reshape((5, -1))
# print(arr)

# Attributes
print(arr.shape, arr.ndim, arr.size, arr.dtype)

# Functions - Our life goal is to avoid using for loops!!!
import timeit
def generate_squares():
    return [x ** 2 for x in range(1000)]  # This is List comprehension (a one line for loop)
def generate_squares_np():
    return np.arange(1000) ** 2

execution_time = timeit.timeit(generate_squares, number=10000)
print(f"list Time taken: {execution_time} seconds")

execution_time2 = timeit.timeit(generate_squares_np, number=10000)
print(f"NP Time taken: {execution_time2} seconds")


arr_sum = np.sum(arr)
arr_mean = np.mean(arr, axis=0)  # axis can be really tricky but really useful for ndimensional data. If I want mean over time, can use axis for that

# Masking - numpy
mask = imgs > -1000
print(mask[0])

imgs_mean = np.mean(imgs[mask])
print(imgs_mean)
# plot_imgs(mask)  # Uncomment if you want to plot your images!


# Critical NumPy topics! TODO didnt have time
# Broadcasting, slicing, indexing, masking!


