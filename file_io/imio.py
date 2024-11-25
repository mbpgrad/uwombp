"""
This Python file is for various image file loading and saving
"""
# Base Python packages
import collections
from datetime import datetime
import glob
import os
import pickle as pkl
import shutil
# Installed packages
import matplotlib
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
import pandas as pd
import pydicom as pyd


# ----------- HELPER FUNCTIONS -----------
def all_equal(iterator):
    iterator = iter(iterator)
    try:
        first = next(iterator)
    except StopIteration:
        return True
    return all(first == x for x in iterator)


def cast_list(test_list, data_type):
    return list(map(data_type, test_list))


def cast_matrix(test_matrix, data_type):
    return list(map(lambda sub: list(map(data_type, sub)), test_matrix))


def remove_duplicates(lst):
    return list(set([i for i in lst]))
# ----------- HELPER FUNCTIONS -----------


def create_dir(path):
    """
    This function will iterate and check each subfolder and if it doesn't exist, create it
    :param path: directory path to be made. Can be multiple new folders
    :return: returns the input path
    """
    if os.path.isdir(path):
        return path
    path_split = path.split('\\')
    folder = ''
    for depth in range(len(path_split)):
        folder = folder + path_split[depth]
        if os.path.isdir(folder):
            pass
        else:
            try:
                os.mkdir(folder)
            except OSError:
                continue
        if depth < len(path_split) - 1:
            folder = folder + '\\'
    print('Directory was made for ' + folder)
    return folder


def hhmmss2time(time: str, date=None):
    if date is None:
        date = '19000101'
    hh, mm, ss = int(time[0:2]), int(time[2:4]), int(time[4:6])
    YYYY, MM, DD = int(date[:4]), int(date[4:6]), int(date[6:8])
    return datetime(YYYY, MM, DD, hh, mm, ss)


def dcm_time_sort(dcms: list, dirs=None):
    """
    Sorts a given list DICOM dataset objects according to date and time
    Intended use is for same slice arrangement; for example, we take slice i5.00 with 10 timepoints and organize in time
    Returns: list of sorted DICOM images, array of timepoints, and an array of timepoint differences and
             if given the sorted list of directories
    """
    dtimes = []
    for dcm in dcms:
        dtimes.append(hhmmss2time(time=str(dcm[0x08, 0x32].value), date=str(dcm[0x08, 0x22].value)))
    temp = dtimes[0]
    deltas = []
    for dtime in dtimes:
        delta = dtime - temp
        deltas.append(delta.total_seconds())
    if isinstance(dirs, list):
        deltas_sorted, dtimes_sorted, dcms_sorted, dirs_sorted = zip(*sorted(zip(deltas, dtimes, dcms, dirs), key=lambda x: x[0]))
    else:
        deltas_sorted, dtimes_sorted, dcms_sorted = zip(*sorted(zip(deltas, dtimes, dcms), key=lambda x: x[0]))

    timepoints = np.array(deltas_sorted)
    timepoints = timepoints - timepoints[0]
    acq_period = [0]
    for ii in range(1, len(timepoints)):
        acq_period.append(timepoints[ii]-timepoints[ii-1])
    acq_period = np.array(acq_period)
    if isinstance(dirs, list):
        return dcms_sorted, timepoints, acq_period, dirs_sorted
    else:
        return dcms_sorted, timepoints, acq_period


def get_affine():
    """
    function for going from DCM to nifti files: need to make an affine array
    https://stackoverflow.com/questions/63451169/how-to-get-affine-information-from-a-dicom-file-in-python
    """
    return  # TODO


def get_n_slices_timepoints_new(dcm_files: list[str]):
    """
    Given a list of pydicom instance sorted loaded dcm files,
    returns the number of slices, number of timepoints and an array of timepoints
    TODO FINISH
    TODO: make sure that missing tags doesnt blow up the program
    """
    n_timepts = 0
    temp_time = [dcm_files[0][0x08, 0x32].value]
    n_dcms = len(dcm_files)
    slice1_loc = dcm_files[0][0x20, 0x1041].value

    study_dates, series_dates, acq_dates, content_dates, study_times, acq_times, series_times, content_times = \
        [], [], [], [], [], [], [], []
    slc_locs = []
    for ds in dcm_files:
        study_dates.append(ds[0x08, 0x20].value)
        series_dates.append(ds[0x08, 0x21].value)
        acq_dates.append(ds[0x08, 0x22].value)
        content_dates.append(ds[0x08, 0x23].value)
        study_times.append(ds[0x08, 0x30].value)
        acq_times.append(ds[0x08, 0x31].value)
        series_times.append(ds[0x08, 0x32].value)
        content_times.append(int(ds[0x08, 0x33].value))
        slc_locs.append(ds[0x20, 0x1041].value)
    values1, counts1 = np.unique(study_dates, return_counts=True)
    values2, counts2 = np.unique(series_dates, return_counts=True)
    values3, counts3 = np.unique(acq_dates, return_counts=True)
    values4, counts4 = np.unique(content_dates, return_counts=True)
    values5, counts5 = np.unique(study_times, return_counts=True)
    values6, counts6 = np.unique(acq_times, return_counts=True)
    values7, counts7 = np.unique(series_times, return_counts=True)
    values8, counts8 = np.unique(content_times, return_counts=True)
    values9, counts9 = np.unique(slc_locs, return_counts=True)
    for ds in dcm_files:
        slice_loc = ds[0x20, 0x1041].value
        time_next = ds[0x08, 0x32].value
        acq_dates.append(ds[0x08, 0x22].value)   # Acquisition Date
        if (temp_time[-1] != time_next) & (slice_loc == slice1_loc):
            """*Note: for brain scans, there is usually a different time point for the top half of the scan and so the 
            'slice_loc == slice1_loc' is very important because we require to go back to the beginning"""
            temp_time.append(time_next)
        if slice_loc == slice1_loc:
            n_timepts += 1
    n_slices = n_dcms / n_timepts

    """temp time is reading [0x08, 0x32] which is in HHMMSS.ff"""
    # TODO need to implement reading date as well in some cases
    time_diff = [0]
    temp_time = cast_list(temp_time, str)
    time0 = temp_time[0]
    acq_period = []
    if '.' in time0:
        for time in temp_time:
            HH, MM, SS, DD = int(time0[0:2]), int(time0[2:4]), int(time0[4:6]), int(time0[7:10])
            hh, mm, ss, dd = int(time[0:2]), int(time[2:4]), int(time[4:6]), int(time[7:10])

            start_t = "%02i:%02i:%02i:%03i" % (HH, MM, SS, DD)
            end_t = "%02i:%02i:%02i:%03i" % (hh, mm, ss, dd)

            t1 = datetime.strptime(start_t, "%H:%M:%S:%f")
            t2 = datetime.strptime(end_t, "%H:%M:%S:%f")
            delta = t2 - t1

            acq_period.append(delta.total_seconds())
            time_diff.append(delta.total_seconds() + time_diff[-1])

            time0 = time
    else:
        for time in temp_time:
            HH, MM, SS = int(time0[0:2]), int(time0[2:4]), int(time0[4:6])
            hh, mm, ss = int(time[0:2]), int(time[2:4]), int(time[4:6])

            start_t = "%02i:%02i:%02i" % (HH, MM, SS)
            end_t = "%02i:%02i:%02i" % (hh, mm, ss)

            t1 = datetime.strptime(start_t, "%H:%M:%S")
            t2 = datetime.strptime(end_t, "%H:%M:%S")
            delta = t2 - t1

            acq_period.append(delta.total_seconds())
            time_diff.append(delta.total_seconds() + time_diff[-1])

            time0 = time
    del time_diff[0]
    if len(acq_period) > 1:
        del acq_period[0]
        acq_period.append(acq_period[-1])

    return int(n_slices), n_timepts, np.around(time_diff, 2), np.around(acq_period, 2)


def get_n_slices_timepoints(dcm_files: list[pyd.Dataset]):  # TODO fix timepoints (messed up in top half has different tp than bottom half) and return slc names
    """
    Given a list of pydicom loaded dcm files,
    returns the number of slices, number of timepoints, an array of timepoints, and an array of the acquisition times
    TODO: make sure that missing tags doesnt blow up the program
    """
    n_timepts = 0
    temp_time = [dcm_files[0][0x08, 0x32].value]
    n_dcms = len(dcm_files)
    slice1_loc = dcm_files[0][0x20, 0x1041].value

    for ds in dcm_files:
        slice_loc = ds[0x20, 0x1041].value
        time_next = ds[0x08, 0x32].value
        if (temp_time[-1] != time_next) & (slice_loc == slice1_loc):
            """*Note: for brain scans, there is usually a different time point for the top half of the scan and so the 
            'slice_loc == slice1_loc' is very important because we require to go back to the beginning"""
            temp_time.append(time_next)
        if slice_loc == slice1_loc:
            n_timepts += 1
    n_slices = int(n_dcms / n_timepts)

    """temp time is reading [0x08, 0x32] which is in HHMMSS.ff"""
    dtimes = []

    for dcm_file in dcm_files:
        dtimes.append(hhmmss2time(time=str(dcm_file[0x08, 0x32].value), date=str(dcm_file[0x08, 0x22].value)))
    temp = dtimes[0]
    deltas = []
    for dtime in dtimes:
        delta = dtime - temp
        deltas.append(delta.total_seconds())
    # we are slice sorted, take for example slc 0, slc n_slc+0, 2*n_slc to get deltas in time order
    deltas = [deltas[ii*n_slices] for ii in range(n_timepts)]

    timepoints = np.array(deltas)                            # timepoints [0, 2, 4, 6, 10, ...]
    timepoints = timepoints - timepoints[0]
    acq_period = [0]
    for ii in range(1, len(timepoints)):
        acq_period.append(timepoints[ii] - timepoints[ii - 1])
    acq_period = np.array(acq_period)                               # duration of scan between points, [2, 2, 2, 4, ...]

    return n_slices, n_timepts, np.around(timepoints, 2), np.around(acq_period, 2)


def transpose(dcm_imgs):
    """
    Given a np array of dicom images, reorder them from
    [slices, timepts, rows, cols] to [slices, rows, cols, timepts]
    @param dcm_imgs:
    :return: returns np array of dcm imgs reordered
    """
    dcm_imgs = np.transpose(dcm_imgs, (0, 3, 2, 1))  # can only transpose 1 axis at a time. Needed
    dcm_imgs = np.transpose(dcm_imgs, (0, 2, 1, 3))  # swap col with row since it was backwards
    return dcm_imgs


# SECTION: Main functions
def fix_headers(hdrs: list):
    """
    given a pydicom.Dataset type object, or a list of ds objects, find all potential problems with the headers that
    will give difficulties in loading, fix them, and return the list of objects
    """
    if not isinstance(hdrs, list):
        hdrs = [hdrs]
    try:  # This catches an issue where no samples per pixel is given and therefore cannot load the pixel_array
        samples_p_pxl = hdrs[0][0x28, 0x02].value
        if samples_p_pxl > 3:
            samples_p_pxl = 1
            for ii in range(len(hdrs)):
                hdrs[ii][0x28, 0x02].value = samples_p_pxl
    except KeyError:
        samples_p_pxl = 1
        for ii in range(len(hdrs)):
            hdrs[ii].add_new([0x28, 0x02], 'US', samples_p_pxl)
    try:
        tranSyntaxUID = hdrs[0][0x02, 0x10].value
    except KeyError:
        if hdrs[0].is_implicit_VR:  # TODO also consider read_implicit_vr needs to be True
            for ii in range(len(hdrs)):
                hdrs[ii].file_meta.TransferSyntaxUID = '1.2.840.10008.1.2'
        elif hdrs[0].is_little_endian:
            for ii in range(len(hdrs)):
                hdrs[ii].file_meta.TransferSyntaxUID = '1.2.840.10008.1.2.1'
    try:
        bitsAllocated = hdrs[0][0x28, 0x100].value
        if bitsAllocated > 64:
            for ii in range(len(hdrs)):
                hdrs[ii][0x28, 0x100].value = 16
                hdrs[ii][0x28, 0x101].value = 16
                hdrs[ii][0x28, 0x102].value = 15
    except KeyError:
        for ii in range(len(hdrs)):
            hdrs[ii].add_new([0x28, 0x100], 'US', 16)
            hdrs[ii].add_new([0x28, 0x101], 'US', 16)
            hdrs[ii].add_new([0x28, 0x102], 'US', 15)
    try:
        photometricInterpretation = hdrs[0][0x28, 0x4].value
        if (photometricInterpretation is None) or (len(photometricInterpretation) == 0):
            photometricInterpretation = 'MONOCHROME2'
            for ii in range(len(hdrs)):
                hdrs[ii][0x28, 0x4].value = photometricInterpretation
    except KeyError:
        for ii in range(len(hdrs)):
            hdrs[ii].add_new([0x28, 0x4], 'CS', 'MONOCHROME2')
    try:
        pixelRepresentation = hdrs[0][0x28, 0x103].value
        if pixelRepresentation > 1:
            for ii in range(len(hdrs)):
                hdrs[ii][0x28, 0x103].value = 1
    except KeyError:
        for ii in range(len(hdrs)):
            hdrs[ii].add_new([0x28, 0x103], 'US', 1)
    try:
        planarConfiguration = hdrs[0][0x28, 0x6].value
    except KeyError:
        for ii in range(len(hdrs)):
            hdrs[ii].add_new([0x28, 0x6], 'US', None)
    return hdrs


def load_dcm_files(dcm_dir: str | list[str],
                   return_info=False, return_dirs_sorted=False,
                   file_exts=None, dcm_rearrange=True):
    """
    @param dcm_dir: directory containing dicom images. If a list of strings are giving, those will be the dcm files
    @param return_info: load info from the DICOM headers
    @param return_dirs_sorted: if True, return includes the list of directories in sorted order
    @param file_exts: a list of file extensions to be used in determining which file to be read in glob-wise
    @param dcm_rearrange: if True, will make sure slices are going in the inferior to superior direction
    :return: returns the dicom file (header + data) given a directory. Following a pydicom object
    NOTE** If the directory contains images of different file types, it will choose the file extension
           of whichever file extension has the most images in that folder. If two have the same number,
           chooses the first
    """
    # TODO if we have given the location of a file, then temp dirs empty, and load that one file
    if isinstance(dcm_dir, str):
        if file_exts is None:
            file_exts = ['.dcm', '.CTDC', '.PTDC', 'IM', 'NMDC', 'Z', '.%i']
        # This snip is for the case that our string IS the dcm file
        dcm_dirs = []
        for file_ext in file_exts:
            if file_ext in dcm_dir.split('\\')[-1][:len(file_ext)]:
                dcm_dirs.append(dcm_dir)
                break
        if len(dcm_dirs) == 0:
            temp_dirs = []
            for ext in file_exts:
                if ext == '.%i':
                    folder_items = glob.glob(r'%s/*' % dcm_dir)
                    files = []
                    for folder_item in folder_items:
                        try:
                            if isinstance(int(folder_item.split('.')[-1]), int) and os.path.isfile(folder_item):
                                files.append(folder_item)
                            # we can't do list comphrehension because 'files' will be empty it goes to except
                            # files = [folder_item for folder_item in folder_items if isinstance(int(folder_item.split('.')[-1]), int) and os.path.isfile(folder_item)]
                        except ValueError:
                            continue
                    temp_dirs.append(files)
                else:
                    temp_dirs.append(glob.glob('%s\\*%s*' % (dcm_dir, ext)))
            lengths = []
            for ii in range(len(file_exts)):
                lengths.append(len(temp_dirs[ii]))
            if isinstance(np.argmax(lengths), np.int64):
                dcm_dirs = temp_dirs[np.argmax(lengths)]
            else:
                dcm_dirs = temp_dirs[np.argmax(lengths)[0]]
    # In this case, we have a list of strings and use those
    elif isinstance(dcm_dir[0], str):
        dcm_dirs = dcm_dir
    dcm_files = [pyd.dcmread(dcm_dirs[ii]) for ii in range(len(dcm_dirs))]
    if len(dcm_files) == 0:
        raise FileNotFoundError('Not properly loading dcm files since %s doesn\'t contain any files with extensions: %s'
                                % (dcm_dir, file_exts))

    inst = []
    try:
        for dcm_file in dcm_files:
            inst.append(int(dcm_file[0x20, 0x13].value))  # instance number
    except KeyError:
        inst = list(np.arange(len(dcm_files)))

    # Sort the files and dirs by instance number
    inst_sorted, dcm_files, dcm_dirs = zip(*sorted(zip(np.array(inst), dcm_files, dcm_dirs), key=lambda x: x[0]))

    # New version: order everything by hand in case the instances are wrong (I'm looking at you XG)
    # Step 1 group our slices together by slc number
    slc_groups = {}
    slc_groups_dirs = {}

    for dcm_file, dcm_dir in zip(dcm_files, dcm_dirs):
        try:
            slc = dcm_file[0x20, 0x1041].value
            if slc is None:
                slc = dcm_file[0x20, 0x32].value[2]
                dcm_file[0x20, 0x1041].value = slc
        except KeyError:
            slc = dcm_file[0x20, 0x32].value[2]
            dcm_file.add_new([0x20, 0x1041], 'DS', slc)
        slc = '%.2f' % slc
        if slc not in slc_groups.keys():
            slc_groups.update({slc: [dcm_file, ]})
            slc_groups_dirs.update({slc: [dcm_dir, ]})
        else:
            slc_groups[slc].append(dcm_file)  # Dictionaries can point to a list, and we can update that list and hence the dictionary
            slc_groups_dirs[slc].append(dcm_dir)
    # Step 2 sort the slices by time
    slc_groups_tsorted = {}  # each slice group sorted by time
    slc_groups_dirs_tsorted = {}  # we need to keep track of the dirs in some instances (example, ITK registration)
    slc_groups_times = {}    # we are going to save all the times, because if we see different lists, it is likely because it is a scanner that needs to change position
    slc_groups_acq_period = {}
    for key in slc_groups:
        slc_group = slc_groups[key]
        dir_group = slc_groups_dirs[key]
        if len(slc_group) > 1:
            dcms_sorted, timepoints, acq_period, dcm_dirs_sorted = dcm_time_sort(slc_group, dirs=dir_group)
        else:
            dcms_sorted = slc_group
            dcm_dirs_sorted = dir_group
            timepoints = []
            acq_period = []
        if key not in slc_groups_tsorted.keys():
            slc_groups_tsorted.update({key: []})
            slc_groups_dirs_tsorted.update({key: []})
            slc_groups_times.update({key: []})
            slc_groups_acq_period.update({key: []})
        slc_groups_tsorted[key].append(dcms_sorted)
        slc_groups_dirs_tsorted[key].append(dcm_dirs_sorted)
        slc_groups_times[key].append(timepoints)
        slc_groups_acq_period[key].append(acq_period)
    # Step 3 sort slices in order of slices
    keys = slc_groups_tsorted.keys()
    keys = [float(key) for key in keys]     # list of time sorted slices [-5, 0, 5, 10, ...]
    vals = slc_groups_tsorted.values()      # list: [[dcm_files in slc0], [slc1]...] tsorted DICOM dataset objects
    dirs = slc_groups_dirs_tsorted.values()
    keys_t_slc_sorted, vals_t_slc_sorted, dirs_t_slc_sorted = zip(*sorted(zip(keys, vals, dirs), key=lambda x: x[0]))

    slc_nums = keys_t_slc_sorted  # slice numbers
    n_slices = len(keys_t_slc_sorted)  # each list corresponds to one slice
    n_tps = len(vals_t_slc_sorted[0])  # each list corresponding to one slice, has n timepoints

    dcm_files = []
    dcm_dirs = []
    for tp in range(n_tps):
        for hdr in range(len(vals_t_slc_sorted[0][0])):
            for slc in range(n_slices):
                dcm_files.append(vals_t_slc_sorted[slc][tp][hdr])
                dcm_dirs.append(dirs_t_slc_sorted[slc][tp][hdr])

    # for slc in range(len(vals_t_slc_sorted)):
    #     for tp in range(len(vals_t_slc_sorted[0])):
    #         for hdr in range(len(vals_t_slc_sorted[0][0])):
    #             dcm_files.append(vals_t_slc_sorted[slc][tp][hdr])
    #             dcm_dirs.append(dirs_t_slc_sorted[slc][tp][hdr])
    # dcm_files = [kk for ii in vals_t_slc_sorted for kk in ii for jj in kk]
    # dcm_dirs = [kk for ii in dirs_t_slc_sorted for kk in ii for jj in kk]
    # dcm_files = [x for xs in vals_t_slc_sorted for x in xs]  # take the list of lists and make it a list of dcm_files
    # dcm_dirs = [x for xs in dirs_t_slc_sorted for x in xs]

    # TODO, we need to handle when the times are different for the upper and lower a bit better (maybe return two times, etc)
    dcm_files = fix_headers(dcm_files)
    info = load_info(dcm_files)         # TODO redundant in some areas, we should change the whole thing

    if return_info and return_dirs_sorted:
        return dcm_files, info, dcm_dirs
    elif return_info and (not return_dirs_sorted):
        return dcm_files, info
    elif (not return_info) and return_dirs_sorted:  # TODO we haven't updated the instance numbers in these files, probably shouldn't until save
        return dcm_files, dcm_dirs
    elif (not return_info) and (not return_dirs_sorted):
        return dcm_files
    else:
        raise ValueError('I have no understanding how you could get here, but send me your email claim your prize')


def load_dcm_imgs(dcm_files, return_info=False, return_hdrs=False, return_dirs_sorted=False, file_exts=None,
                  dcm_rearrange=True):
    """
    DICOM image loader, can provide the directory containing the DICOM files, or a list of strings which
    @param dcm_files: directory containing dicom images of different extensions or a list of str names or a list of pydicom files
    @param return_info: will return another output if True that will be the important header info
    @param return_hdrs: will return another output if True that is the header and data info from every file in the dir
    @param return_dirs_sorted:
    @param file_exts: list of file extensions for loading DICOM files, default list is in load_dcm_files
    @param dcm_rearrange: True by default, will reorganize the DICOM files to be in correct order
    :return: returns properly scaled arrays of values corresponding to the stored values in the dicom files
             returns dcm_imgs, info, dcm_files if all three are selected
    """
    if isinstance(dcm_files, str) or (isinstance(dcm_files, list) and isinstance(dcm_files[0], str)):
        if return_dirs_sorted:
            dcm_files, info, dcm_dirs = load_dcm_files(dcm_files, return_info=True,
                                                 return_dirs_sorted=return_dirs_sorted, file_exts=file_exts)
        else:
            dcm_files, info = load_dcm_files(dcm_files, return_info=True,
                                       return_dirs_sorted=return_dirs_sorted, file_exts=file_exts)
    else:
        info = load_info(dcm_files)
    n_slices = info.get('n_slices')
    n_timepts = info.get('n_timepts')
    n_rows = info.get('n_rows')
    n_cols = info.get('n_cols')

    dcm_imgs = np.zeros((n_slices * n_timepts, n_rows, n_cols))
    for ii in range(n_slices * n_timepts):  # need to adjust our pixel arrays by the rescaling factors
        dcm_imgs[ii, :, :] = dcm_files[ii].pixel_array.astype(np.float64) * info.get('r_slope')[ii] + info.get('r_int')[ii]

    # we reshape this way since we have (n_slices*n_timepoints, n_rows, n_cols) and so we separate the first index
    dcm_imgs = np.reshape(dcm_imgs, (n_slices, n_timepts, n_rows, n_cols), order='F')  # you need 'F'
    dcm_imgs = transpose(dcm_imgs)  # now is (n_slices, n_rows, n_cols, n_timepts)

    # If we only have 1 time point, return back a 3D image instead of 4D
    if dcm_imgs.shape[-1] == 1:
        dcm_imgs = dcm_imgs.reshape(dcm_imgs.shape[:-1])

    if not return_info and not return_hdrs:
        if return_dirs_sorted:
            return dcm_imgs, dcm_dirs
        return dcm_imgs
    elif return_info and not return_hdrs:
        if return_dirs_sorted:
            return dcm_imgs, info, dcm_dirs
        return dcm_imgs, info
    elif return_hdrs and not return_info:
        if return_dirs_sorted:
            return dcm_imgs, dcm_files, dcm_dirs
        return dcm_imgs, dcm_files
    elif return_info and return_hdrs:
        if return_dirs_sorted:
            return dcm_imgs, info, dcm_files, dcm_dirs
        return dcm_imgs, info, dcm_files
    else:
        raise TypeError('Problem with outputting the dcm imgs and/or info, and/or headers from loading files')


def load_info(dcm_files):
    """
    Given a dicom file with a dicom header, will return parameters of interest as a dictionary
    @param dcm_files: can be a string which is the directory for the dcm files,
    or can be a list of the loaded dcm files
    :return: dictionary with the consistent important info on the study
    """
    if isinstance(dcm_files, str):
        dcm_files = load_dcm_files(dcm_files)
    ds = dcm_files[0]
    try:
        slice_thickness = ds[0x18, 0x50].value  # Slice thickness [mm]
    except KeyError:  # Try and get the slice thickness from the position differences
        slice_thickness = abs(dcm_files[0][0x20, 0x1041].value - dcm_files[1][0x20, 0x1041].value)
        print('Slice thickness 0018, 0050 was not found! Taken from Slice Location Differences, 0x20, 0x1041: ', slice_thickness)

    n_rows = ds[0x28, 0x10].value  # Number of rows
    n_cols = ds[0x28, 0x11].value  # Number of cols
    pxl_spacing = ds[0x28, 0x30].value  # Pixel spacing returns a tuple
    vox_size = slice_thickness * pxl_spacing[0] * pxl_spacing[1] / 1000  # 1000 for mm3 to cm3
    # try:
    #     fov = ds[0x18, 0x1100].value  # Reconstruction diameter (scan FOV)
    # except KeyError:
    #     try:
    #         fov = ds[0x18, 0x90]  # Scan FOV
    #     except KeyError:
    #         fov = np.round(n_rows * pxl_spacing[0])
    fov = np.round(n_rows * pxl_spacing[0])
    r_int = []
    r_slope = []
    img_pos = []
    slc_loc = []
    for hdr in dcm_files:
        r_int.append(hdr[0x28, 0x1052].value)  # Rescale intercept
        r_slope.append(hdr[0x28, 0x1053].value)  # Rescale slope
        img_pos.append(hdr[0x20, 0x32].value)  # Image position
        slc_loc.append(np.around(hdr[0x20, 0x1041].value, 2))
    n_slices, n_timepts, timepts, acq_period = get_n_slices_timepoints(dcm_files)
    slc_loc = np.array(slc_loc)
    slc_loc = slc_loc[:n_slices]
    info = {
        'slice_thickness': slice_thickness, 'n_rows': n_rows, 'n_cols': n_cols, 'pxl_spacing': pxl_spacing, 'vox_size':
            vox_size, 'acq_period': acq_period, 'fov': fov, 'r_int': r_int, 'r_slope': r_slope, 'n_slices': n_slices, 'n_timepts': n_timepts,
        'timepts': timepts, 'img_pos': img_pos[0], 'slc_loc': slc_loc
    }

    info_cp = info.copy()
    if all_equal(info.get('r_slope')):
        info_cp['r_slope'] = info.get('r_slope')[0]
    else:
        r_slope_reduced = r_slope[:n_slices]
        info_cp['r_slope'] = r_slope_reduced
    if all_equal(info.get('r_int')):
        info_cp['r_int'] = info.get('r_int')[0]
    if all_equal(info.get('timepts')):
        info_cp['timepts'] = info.get('timepts')[0]
    if all_equal(info.get('acq_period')):
        info_cp['acq_period'] = info.get('acq_period')[0]
    print(info_cp)
    return info


def load_pkl(fp: str):
    print('Reading file', fp)
    with open(fp, 'rb') as pklfile:
        data = pkl.load(pklfile)
        return data


def load_nifti(fp: str, return_hdr=False):
    """
    returns niftii object
    """
    n1_img = nib.load(fp)
    hdr = n1_img.header
    if return_hdr:
        return np.array(n1_img.dataobj), hdr
    else:
        return np.array(n1_img.dataobj)


def save_dcm_files(dcm_imgs, hdrs, output_dir, filename: str | list,
                   nrows, ncols, scale=1, rs: float = 1, ri: float = 0, pxl_spacing=-1,
                   img_positions=-1, img_ori=-1,
                   study_desc=None,
                   create_new_dir = True, save_one_file = False, anonymize=False):
    """
    TODO: make the rescale slope and intercept automatically calculated to fit all the data into a 16bit
          which is 66500 integers with as much precision as possible
    TODO: create UID for anon? https://dicom.nema.org/medical/dicom/current/output/html/part05.html#chapter_B
    @param dcm_imgs:
    @param hdrs:
    @param output_dir:
    @param filename: can be a string that will be numerated and distributed to each file or a list of filenames
    @param nrows:
    @param ncols:
    @param scale:
    @param rs: the rescale slope with a default value of 1
               if rs = -1, calculates optimal rs
               if rs = 0, leaves rs as what is in the header
    @param ri:
    @param study_desc:
    :return:
    """
    """ Given a header to work with (Not from scratch)"""
    if dcm_imgs.ndim == 4:
        print('We need to adjust the time that is being saved potentially for these hdrs')  # TODO
    dcm_imgs = dcm_imgs * scale
    if study_desc is None:
        try:
            study_desc = hdrs[0][0x08, 0x1030].value
        except KeyError:
            study_desc = ' '
    if create_new_dir:
        output_dir = create_dir(r'%s\maps' % output_dir)
    else:
        output_dir = create_dir(output_dir)
    os.chdir(output_dir)
    if rs == -1:
        maxval = np.amax(dcm_imgs)
        rs = maxval / 32760  # unsigned int can be 2 * 32760
    if len(dcm_imgs) == 1:
        if isinstance(filename, str):
            filename = ['%s.dcm' % filename]
        else:
            filename = ['img.dcm']
    elif isinstance(filename, str):
        filename = ['%s_%s.dcm' % (filename, str(ii).zfill(5)) for ii in range(dcm_imgs.shape[0])]
    else:
        filename = ['img_%s.dcm' % (str(ii).zfill(5)) for ii in range(dcm_imgs.shape[0])]
    if not save_one_file:
        for ii in range(dcm_imgs.shape[0]):
            ds = hdrs[ii]
            try:
                ds[0x08, 0x1030].value = study_desc  # Study description
            except KeyError:
                ds.add_new([0x08, 0x1030], 'LO', study_desc)
            if rs == 0:
                rs = ds[0x28, 0x1053].value
                ri = ds[0x28, 0x1052].value
            try:
                recon_diam = ds[0x18, 0x1100].value  # RECON DIAM
            except KeyError:
                try:
                    recon_diam = ds[0x18, 0x90]  # FOV
                    ds.add_new([0x18, 0x1100], 'DS', recon_diam)
                except KeyError:
                    recon_diam = np.ceil(nrows * pxl_spacing[0])
                    ds.add_new([0x18, 0x1100], 'DS', recon_diam)
            try:
                some_iter = iter(pxl_spacing)
            except TypeError:
                try:
                    recon_diam = ds[0x18, 0x1100].value
                    pxl_spacing = [recon_diam / float(ncols), recon_diam / float(nrows)]
                except KeyError:
                    raise KeyError(r'Must give an iterable for pixel spacing since ds[0x18, 0x1100].value (reconstruction diameter) is not available in header')

            arr1 = (dcm_imgs[ii, :, :] - ri).astype(np.float64)
            arr2 = arr1 / rs
            arr3 = arr2.astype(np.int16)

            # arr = np.int16((dcm_imgs[ii, :, :] - ri).astype(np.float64) / rs)
            ds.PixelData = arr3.tobytes()

            ds.Rows = nrows
            ds.Columns = ncols
            try:
                ds[0x28, 0x1052].value = ri  # rescale intercept
            except KeyError:
                ds.add_new([0x28, 0x1052], 'DS', ri)
            try:
                ds[0x28, 0x1053].value = rs  # rescale slope
            except KeyError:
                ds.add_new([0x28, 0x1053], 'DS', rs)
            try:  # experimental: this is correct but causes an issue with XG's CTP when loading dcms
                ds[0x20, 0x13].value = ii+1  # instance number
            except KeyError:
                ds.add_new([0x28, 0x1052], 'IS', ii+1)
            try:  # This fixes issue where no samples per pixel is given and therefore, pixel_array can't be loaded
                samples_p_pxl = ds[0x28, 0x02].value
            except KeyError:
                samples_p_pxl = 1
                ds.add_new([0x28, 0x02], 'US', samples_p_pxl)
            ds[0x28, 0x30].value = [pxl_spacing[0], pxl_spacing[1]]

            # if anonymize:  # TODO finish anonymizataion,
            #     # TODO we should maybe have a clean standard DCM header
            #     # https://pydicom.github.io/pydicom/dev/auto_examples/metadata_processing/plot_anonymize.html
            #     # https://www.imaios.com/en/resources/blog/dicom-anonymization
            #     ds.walk(person_names_callback)
            #     # data_elements = ['PatientID',
            #     #                  'PatientBirthDate']
            #     # for de in data_elements:
            #     #     print(ds.data_element(de))
            pyd.dcmwrite(filename=filename[ii], dataset=ds, write_like_original=True)

    else:
        ds = hdrs
        try:
            ds[0x08, 0x1030].value = study_desc  # Study description
        except KeyError:
            ds.add_new([0x08, 0x1030], 'LO', study_desc)

        try:
            recon_diam = ds[0x18, 0x1100].value
            if pxl_spacing == -1:
                pxl_spacing = [recon_diam / float(ncols), recon_diam / float(nrows)]
        except KeyError:
            pass
        # pxl_spacing = [recon_diam / float(ncols), recon_diam / float(nrows)]

        arr1 = (dcm_imgs[:, :, :] - ri).astype(np.float64)
        arr2 = arr1 / rs
        arr3 = arr2.astype(np.int16)

        # arr = np.int16((dcm_imgs[ii, :, :] - ri).astype(np.float64) / rs)
        ds.PixelData = arr3.tobytes()

        ds.Rows = nrows
        ds.Columns = ncols
        ds[0x28, 0x1052].value = ri  # rescale intercept
        ds[0x28, 0x1053].value = rs  # rescale slope
        ds[0x28, 0x30].value = [pxl_spacing[0], pxl_spacing[1]]
        pyd.dcmwrite(filename='%s_all.dcm' % filename, dataset=ds, write_like_original=True)
    # if dcm_imgs.ndim == 3:
    #     if (dcm_imgs.shape[0] != hdrs.shape[0]) & (hdrs.shape[0] > dcm_imgs.shape[0]):
    #         #  Make it so that it takes the first time point hdrs
    #         raise ValueError('Headers provided is not for the number of dcm imgs provided')
    # elif dcm_imgs.ndim == 4:
    #     print('work')
    # print('need to make sure headers are taken from original with updated description')


def save_pkl(data: np.ndarray, outdir: str, filename='data.pkl'):
    if '.pkl' in filename:
        pass
    else:
        filename += '.pkl'
    outdir = create_dir(outdir)  # Make the dir if it doesn't exist already
    with open("%s\\%s" % (outdir, filename), 'wb') as pklfile:
        pkl.dump(data, pklfile)
    print("%s\\%s successfully pickled" % (outdir, filename))
    return
