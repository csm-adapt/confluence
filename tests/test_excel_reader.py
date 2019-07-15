import pandas as pd
from pathlib import Path
from ExcelReader import Excel_reader


def expected_file_contents(finalFile):
    ifs = pd.read_excel(finalFile)
    return ifs

def destination_file_contents(destination):
    ifs = pd.read_excel(destination)
    return ifs

def test_LocalReader():
    """
    Function: Creates an instance of the Excel_reader class and feeds it the four separate excel files. These files
    were augmented according to the guildlines in the email.
    :return: none
    """
    fileFolder = Path("C:/Users/Alex/Documents/Excel_Reader_Tests")

    file1 = fileFolder / 'LHM_build_1.xlsx'
    file2 = fileFolder / 'LHM_build_2.xlsx'
    file3 = fileFolder / 'LHM_build_3.xlsx'
    file4 = fileFolder / 'LHM_build_4.xlsx'
    finalFile = fileFolder / 'LHM_build_final_.xlsx'
    destination = fileFolder / 'LHM_build_destination.xlsx'

    reader = Excel_reader(file1, file2, file3, file4)
    reader.merge()
    reader.write()
    expected = expected_file_contents(finalFile)
    actual = destination_file_contents(destination)

    assert actual == expected


test_LocalReader()
