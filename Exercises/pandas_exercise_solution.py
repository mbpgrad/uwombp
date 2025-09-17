r"""
Written by ddesarn@uwo.ca
this file is an exercise with some guidance. The goal is how would one use Pandas or Excel/CSV file reading and writing
in a practical medical image related problem.

The problem: we want to make a spreadsheet of patient data, in this case: ID, sex, age, and weight from our medical images.
But I want to do this for 100+ patients, so let's do it automatically with a script.

Data will come from test_files\pandas_exercise_files
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
    """
    # ds for DataSet
    ds = pydicom.dcmread(fp)

    # These are hexidecimal tags that describe an element in the DICOM header, as DICOM is supposed to standardize info
    patient_id = ds.PatientID
    sex = ds[0x10, 0x0040].value
    age = ds[0x10, 0x1010].value
    weight = ds[0x10, 0x1030].value

    return patient_id, sex, age, weight


def main_pandas_exercise(data_foldername=r'test_files\pandas_exercise_files', search_pattern_string='*.dcm'):
    """
    This is our main function that we call to run everything we need for the objective
    - get the patient files
    - load the info
    - write out an Excel file with this info
    """

    os.chdir('..')               # This goes up one directory from our current working directory 'PATH\...\Tutorials'
    current_dir = os.getcwd()
    data_dir = rf'{current_dir}\{data_foldername}'
    fps = glob.glob(rf'{data_dir}\{search_pattern_string}')

    infos = []
    for fp in fps:
        info = load_dcm_sex_age_weight(fp)
        infos.append(info)

    # print(infos)
    df = pd.DataFrame(infos, columns=['PatientID', 'Sex', 'Age', 'Weight (kg)'])
    print(df)

    # Change our working directory to the data outputs folder
    os.chdir(data_dir)

    # Save the DataFrame to an Excel file
    df.to_excel('pandas_exercise_output.xlsx', index=False)


main_pandas_exercise()
