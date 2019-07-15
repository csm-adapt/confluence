import pandas as pd
from pathlib import Path
from ExcelReader import Excel_reader


def expected_file_contents(finalFile):
    ifs = pd.read_excel(finalFile)
    return ifs


def test_LocalReader():
    fileFolder = Path("C:/Users/Alex/Documents/Excel_Reader_Tests")

    file1 = fileFolder / 'LHM_build_1.xlsx'
    file2 = fileFolder / 'LHM_build_2.xlsx'
    file3 = fileFolder / 'LHM_build_3.xlsx'
    file4 = fileFolder / 'LHM_build_4.xlsx'
    finalFile = fileFolder / 'LHM_build_final_.xlsx'

    reader = Excel_reader(file1, file2, file3, file4)
    mergedFile = reader.merge()
    expected = expected_file_contents(finalFile)
    assert mergedFile == expected


test_LocalReader()
