r"""
Written by ddesarn@uwo.ca
this file is an exercise with some guidance. The goal is how would one use Pandas or Excel/CSV file reading and writing
in a practical medical image related problem.

The problem: we want to make a spreadsheet of patient data, in this case: ID, sex, age, and weight from our medical images.
But I want to do this for 100+ patients, so let's do it automatically with a script.

Data will come from test_files\pandas_exercise_files
Some help is provided below to help structure your solution
"""


import glob
import pydicom
import pandas as pd
import openpyxl
import os


def load_dcm_sex_age_weight(fp):
    """
    Given a filepath to a DICOM image, loads it using Pydicom, accesses the ID, sex, age, and weight elements, returns
    a list of the three elements.
    :param fp: filepath to a DICOM image file (usually, a .dcm extension, but can have others!)

    Tips:
    - Use pydicom.dcmread to read in the DICOM files as a DataSet object
    - DICOM headers have tags that you can look up, example, sex is [0x10, 0x0040]
    - use .value when accessing a DataSet element to get the value instead of the DataSetElement object
    """


    return # patient_id, sex, age, weight


def main_pandas_exercise(data_foldername=r'test_files\pandas_exercise_files'):
    """
    This is our main function that we call to run everything we need for the objective
    - get the patient files
    - load the info
    - write out an Excel file with this info
    """
    # This is to get the directory of the uwombp files automatically
    os.chdir('..')               # This goes up one directory from our current working directory 'PATH\...\Tutorials'
    current_dir = os.getcwd()
    data_dir = rf'{current_dir}\{data_foldername}'

    os.chdir(data_dir)  # Change our working directory to the data outputs folder (when we save, it will save here!)

    # TODO - things to do:
    #        1. Get the list of filepaths in the pandas_exercise_files directory - tip: use glob.glob
    #        2. Finish the load_dcm_sex_age_weight function to load a DICOM file and return the 4 things we want
    #        3. Iterate through our list of files and load in their info and save them to a list
    #        4. Save outputs to an Excel file


main_pandas_exercise()
