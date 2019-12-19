import sys
import argparse
import pandas as pd
import numpy as np
import os
import inspect
from itertools import product
from .io.excel import ExcelReader
from .Read import read
from .validator import setup_validator
from .check_args import check
from .global_variables import get_sample_name_column
from .dataframe import *


def generate_merge_args(description):
    def parse_args(args):

        if isinstance(args,list):
            parser = argparse.ArgumentParser(description = description)
        else:
            parser = args

        parser.add_argument('infiles', nargs='*', help='input file name with no file type')
        parser.add_argument('-o', '--output', help='output file name')
        parser.add_argument('-i', '--input', nargs=2, help='input file name with accompanying file type', action='append')
        parser.add_argument('-m', '--mergedefault', help='default solution to merge conflicts')
        parser.add_argument('--interactive', action='store_true', help='make the program prompt user for input in case of conflict')
        parser.add_argument('-s', '--sheetname', help='Specify a default sheetname in case writing to an xlsx file')
        parser.add_argument('--outputformat', help='specify output file type')
        parser.add_argument('-q', '--quiet', action='store_true', help='Should a merge conflict happen, default to abort')
        parser.add_argument('-k', '--key', help='Specify the name of the smaple name column', default='Sample Name')

        if isinstance(args, list):
            return parser.parse_args(args)
    return parse_args


def merge_files(args, sheetname='Sheet1'):
    """
    Function: This does the same thing as 'run()' but instead of writing the dataframes to a file, it returns the
    dataframe.
    :param args:
    :return:
    """
    args = create_parser(args)
    file_df = create_df_of_all_infiles(args)
    file_df = file_df[file_df['sheetname'] == sheetname]
    merged = merge_dataframes(file_df, sheetname)
    return merged


def guess_file_type(filename):
    """
    :param filename: name of the file
    :return: the file handle that presumably tells the type of the file
    """
    return os.path.splitext(filename)[1].strip('.')


def merge_dataframes(file_df, sheetname):
    dfs = add_filename_columns_to_dfs(file_df)
    df = compare_and_merge_multiple_dfs(dfs, sheetname)
    df = drop_filename_column_from_df(df)
    df = sort_values(df)
    return df


def compare_and_merge_multiple_dfs(dfs, sheetname):
    mergedDf = create_empty_df()
    for df in dfs:
        mergedDf = check_two_dfs_for_merge_conflict(mergedDf, df, sheetname)
        mergedDf = fix_dataframe(mergedDf)
    return mergedDf


def get_list_of_dataframes_from_file_df(file_df):
    dfs = list(file_df['dataframe'])
    return dfs


def get_list_of_dataframes_from_file_df_by_specific_sheet(file_df, sheetname):
    df_same_sheet = file_df[file_df['sheetname'] == sheetname]
    dfs = get_list_of_dataframes_from_file_df(df_same_sheet)
    return dfs


def add_filename_columns_to_dfs(file_df):
    dfs = get_list_of_dataframes_from_file_df(file_df)
    filenames = list(file_df['filename'])
    for i in range(len(file_df)):
        dfs[i] = add_filename_column_to_single_df(dfs[i], filenames[i])
    return dfs


def drop_filename_column_from_df(df):
    df = df.drop('Filename', axis=1)
    return df


def add_filename_column_to_single_df(df, filename):
    length = len(df)
    filenameArray = [filename]*length
    df['Filename'] = filenameArray
    return df


def sort_values(df):
    if df.empty:
        return df
    return df.sort_values([get_sample_name_column()]).reset_index(drop=True)


def create_directory(folderName):
    try:
        os.mkdir(folderName)
    except FileExistsError:
        raise FileExistsError(f"Folder named '{folderName}' already exists. Specify a different output name.")


def get_sheetnames(file):
    """
    Function: Takes an array of excel files and finds the sheetnames of all of them. Then it eliminates the duplicates
    and returns a list of each sheetname.
    :param files: all the files being accessed
    :return: a list of every sheet name that is being used
    """
    arr = ExcelReader(file).sheetnames()
    return list(dict.fromkeys(arr))
    # Eliminates duplicate names while still preserving order. That is because when creating a dictionary, python
    # automatically gets rid of duplicate keys.


def get_file(fname, ftype):
    """
    Function: If the user enters a file name with no extention and a file type, go ahead and join them together.
    Otherwise, just return the original file name
    :param fname:
    :param ftype:
    :return: file name
    """
    if not os.path.splitext(fname)[1].strip('.') and ftype:
        return os.path.join(os.path.splitext(fname)[0] + "." + ftype.strip('.'))
    # If the file extention does not exist and the file type does exist, join them together.
    else:
        return fname


def create_df_of_all_infiles(args):
    """
    Function: This creates a dataframe containing the information for each file read in. Let's say we read in three
    files: file1.xlsx, file2.xlsx, and file3.txt. Each of the excel files has just one sheet, 'Hardness'. We want the dataframe
    to look like this:

    Filename          Dataframe               Type    Sheetname
    'file1.xlsx'    <dataframe for file1>     xlsx    'Hardness'
    'file2.xlsx'    <dataframe for file2>     xlsx    'Hardness'
    'file3.txt'     <dataframe for file3>     txt     'Sheet1'

    Notice how the sheet name for file3.txt is 'Sheet1', we have a function that allows the user to specify the sheet
    name for non-excel files, but if no name is specified it defaults to 'Sheet1'

    There will be one row for each dataframe, but not necessarily one row for each file name. For example, if we were
    to read in a fourth file, 'file4.xlsx', with two sheets in it, 'Hardness' and 'Spectroscopy', our file dataframe
    will look like this:

    Filename              Dataframe                      Type    Sheetname
    'file1.xlsx'    <dataframe for file1>                xlsx    'Hardness'
    'file2.xlsx'    <dataframe for file2>                xlsx    'Hardness'
    'file3.txt'     <dataframe for file3>                txt     'Sheet1'
    'file4.xlsx'    <first dataframe for file4>          xlsx    'Hardness'
    'file4.xlsx'    <second dataframe for file4>         xlsx    'Spectroscopy'


    The reason I decided to do it this way is so that we can pass the information to other functions easier . We can
    simply call df['dataframe'] and get a list of all the dataframes to write to a file.
    :param args: The argparse object containing all filenames.
    :return: the file dataframe
    """
    df_rows_from_args_infile = [file_df_row(file, guess_file_type(file)) for file in args.infiles] if args.infiles else []
    # Creates an array of each row of the file dataframe. It calls the function 'create_file_df()' and gives it the
    # file name and guesses the file type.
    df_rows_from_args_input = [file_df_row(file, ftype) for ftype, file in args.input] if args.input else []
    files = join_many_dataframes(df_rows_from_args_input + df_rows_from_args_infile)
    return files





def add_row_to_file_df(file_df, filename, dataframe, ftype, sheetname):
    """
    Function: Adds a row to the file dataframe. All we have to do is give it the filename, dataframe, type, and sheet
    name and it appends it to the dataframe

    :param file_df: The dataframe of all the files, corresponding dataframes, types, and sheetnames
    :param filename: file name
    :param dataframe: dataframe corresponding to the file name
    :param ftype: type
    :param sheetname: sheet name
    :return: dataframe with the new row
    """
    return file_df.append({'filename': filename,
                      'dataframe': dataframe,
                      'type': ftype,
                      'sheetname': sheetname
                      }, ignore_index=True)


def file_df_row(filename, ftype):
    """
    Function: creates new row in te file dataframe. It figures out the file name, corresponding dataframe, type, and
    sheetname, then puts them all into a row in the file dataframe.

    :param filename: name of the file being passed to the function
    :param ftype: type fo the file
    :return: dataframe containing name, dataframe, type, and any sheetnames of the file
    """
    file_df = create_empty_df(['filename', 'dataframe', 'type', 'sheetname'])
    sheets = get_sheetnames(filename) if ftype == 'xlsx' else [get_txt_sheetname()]
    # if the file type is xlsx, get all the sheetnames as a list. Otherwise, it sets the sheetname as the txtSheetname
    # variable, which is a global variable set by the user. If the user does not specify a sheetname for non-excel
    # files, it defaults to 'Sheet1'.
    for sheetname in sheets:
        df = get_dataframe(filename, ftype, sheetname)
        # This is where we finally get to read the dataframe for the file. The read() function determines what reader
        # to use, and returns the file as a dataframe.
        file_df = add_row_to_file_df(file_df, filename, df, ftype, sheetname)
    # Some files have multiple sheetnames and will therefore have multiple rows in the file dataframe. This adds a new
    # row for each sheet.
    return file_df


def get_dataframe(filename, ftype, sheetname):
    validate = setup_validator()
    # Look under the setup_validator function, I explain how the validator works.
    df = read(filename, ftype, sheetname).as_dataframe()
    if not df.empty:
        df = validate(df, filename, sheetname, ftype)
    return df


def create_parser(args):
    """
    function: set up a parser with all the args the user passes to the function
    :return: parser containing all the args
    """
    parser = argparse.ArgumentParser(description='parse arguments')
    parser.add_argument('infiles', nargs='*', help='input file name with no file type')
    parser.add_argument('-o', '--output', help='output file name')
    parser.add_argument('-i', '--input', nargs=2, help='input file name with accompanying file type', action='append')
    parser.add_argument('-m', '--mergedefault', help='default solution to merge conflicts')
    parser.add_argument('--interactive', action='store_true', help='make the program prompt user for input in case of conflict')
    parser.add_argument('-s', '--sheetname', help='Specify a default sheetname in case writing to an xlsx file')
    parser.add_argument('--outputformat', help='specify output file type')
    parser.add_argument('-q', '--quiet', action='store_true', help='Should a merge conflict happen, default to abort')
    parser.add_argument('-k', '--key', help='Specify the name of the sample name column', default='Sample Name')
    return parser.parse_args(args)


def get_sheetnames_from_file_df(file_df):
    sheets = list(file_df['sheetname'].drop_duplicates())
    return sheets