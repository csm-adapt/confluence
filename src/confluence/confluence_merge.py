"""
confluence-merge merges data from two or more input files. This performs
several checks:

1. The columns in each table
1. Unique rows (a.k.a. records) from each
"""

import os
import sys
import argparse
import logging
import pandas as pd
import numpy as np
from .merge import MergeActions
from .merge import InfilesActions
from .merge import InteractiveActions
from .io import read
from .io import write
from .validator import QMDataFrameValidator
from .check_args import check


__author__ = "Branden Kappes"
__copyright__ = "Branden Kappes"
__license__ = "mit"

_logger = logging.getLogger(__name__)


def parse_args(args):
    # Is parse_args being called as a console script, or as a subcommand?
    if isinstance(args, list):
        # console script? Create a new parser.
        parser = argparse.ArgumentParser(description=__doc__)
    else:
        # subcommand? We've already created the necessary subcommand.
        parser = args

    parser.add_argument('infiles',
                        nargs='*',
                        help='Names of files to be merged.',
                        action=InfilesActions)
    parser.add_argument('-i', '--input', nargs=2, action='append')
    parser.add_argument('-o', '--output',
                        help='Output file name.')
    parser.add_argument('-m', '--mergedefault',
                        action=MergeActions,
                        default=MergeActions.abort,
                        help='Default method to solve merge conflicts. '
                             'Options: abort, first, second, join, mean. Default: abort.')
    parser.add_argument('--interactive',
                        action='store_true',
                        help='Prompt user for input in case of conflict.')
    parser.add_argument('-s', '--sheetname',
                        help='Specify a default sheetname (Excel file).')
    parser.add_argument('--ofmt',
                        help='Specify the format of the output file.')
    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help='Should a merge conflict happen, default to abort')
    parser.add_argument('-k', '--key',
                        help='Specify the column name used as the primary key. '
                             'Default: Sample Name',
                        default='Sample Name')

    if isinstance(args, list):
        return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


class Metadata:
    filename = None
    ftype = None
    dataframe = pd.DataFrame()
    sheetname = None


def execute(args):
    """
    Function: This is the function called when the confluence_merge.py is used in the terminal.
    :param args: An array of files to be merged
    :return: None
    """
    args = parse_args(args)
    args = get_infiles(args)
    args = check(args)
    metadatalist = get_metadata_list(args)
    outfile = get_file(args.output, args.ofmt)
    mergedlist = merge_metadatalist(args, metadatalist)
    write(mergedlist, outfile, args.ofmt)


def merge_metadatalist(args, metadatalist):
    merged_list = []
    sheetnames = list(dict.fromkeys([a.sheetname for a in metadatalist]))
    for sheet in sheetnames:
        metadata = Metadata()
        metadatalist = [a for a in metadatalist if a.sheetname == sheet]
        metadata.sheetname = sheet
        metadata.dataframe = merge_dataframes(args, metadatalist, sheet)
        merged_list.append(metadata)
    return merged_list


def get_infiles(args):
    """
    Function: This takes the files from arg
    :param args:
    :return:
    """
    if args.input:
        for ftype, filename in args.input:
            Values = InfilesActions.Values()
            Values.filename = filename
            Values.ftype = ftype
            args.infiles = args.infiles + [Values]
    return args


def get_metadata_list(args):
    metadatalist = []
    for file in args.infiles:
        for sheet in get_sheetnames(args, file.filename, file.ftype):
            metadata = Metadata()
            metadata.filename = file.filename
            metadata.ftype = file.ftype
            metadata.dataframe = get_dataframe(args, file.filename, file.ftype, sheet)
            metadata.sheetname = sheet
            metadatalist.append(metadata)
    return metadatalist


def get_sheetnames(args, filename, ftype):
    ftype = guess_file_type(filename) if ftype is None else ftype
    if ftype == 'xlsx':
        return get_sheetnames_xlsx(filename)
    return [args.sheetname]


def get_sheetnames_xlsx(filename):
    try:
        reader = read(filename)
        return reader.sheetnames()
    except:
        raise ValueError(f"'{filename}' has no sheets.")


def merge_files(args):
    """
    Function: This does the same thing as 'execute()' but instead of writing the dataframes to a file, it returns the
    dataframe.
    :param args:
    :return:
    """
    args = parse_args(args)
    args = get_infiles(args)
    metadatalist = get_metadata_list(args)
    mergedlist = merge_metadatalist(args, metadatalist)
    return mergedlist[0].dataframe


def merge_dataframes(args, metadatalist, sheetname):
    """
    Function: Takes the file dataframe (the big dataframe containing the filenames, corresponding dataframes, file
    type, and sheet names of each input file) and gets the merged dataframe. It does this in the following order:
    1.  Makes a list of the dataframes, and adds a filename column. This way, if there is a merge conflict, it can
        display to the user which input file created the conflict.
    2.  Feeds the list of dataframes to 'compare_and_merge_multiple_dfs'. This function returns a merged dataframe
    3.  Since we no longer need to know which line in the merged dataframe came from which input file, it deletes the
        column
    4.  Sorts the values by sample name. This may be taken off in the future.
    :param file_df: file dataframe with all the metadata
    :param sheetname: sheetname being merged
    :return: merged dataframe
    """
    dfs = add_filename_columns_to_dfs(metadatalist)
    df = compare_and_merge_multiple_dfs(args, dfs, sheetname)
    df = drop_filename_column_from_df(df)
    df = sort_values(args, df)
    return df


def compare_and_merge_multiple_dfs(args, dfs, sheetname):
    """
    Function: takes a list of dataframes and merges them.
    :param dfs: list of dataframes
    :param sheetname: sheetname being merged
    :return: merged dataframe
    """
    mergedDf = create_empty_df()
    for df in dfs:
        mergedDf = check_two_dfs_for_merge_conflict(args, mergedDf, df, sheetname)
        mergedDf = fix_dataframe(args, mergedDf)
    return mergedDf


def add_filename_columns_to_dfs(metadatalist):
    """
    Function: Takes the individual dataframes from the file dataframe and their corresponding filenames and adds a
    filename column to the dataframe. Each row of each dataframe came from the same file, so the filename column will
    be homogenous for a single dataframe.
    :param file_df:
    :return: list of dataframes with a filename column added to each
    """
    dfs = [obj.dataframe for obj in metadatalist]
    filenames = [obj.filename for obj in metadatalist]
    for i in range(len(dfs)):
        dfs[i] = add_filename_column_to_single_df(dfs[i], filenames[i])
    return dfs


def drop_filename_column_from_df(df):
    """
    Function: Removes the filename column
    :param df: dataframe with a filename column
    :return: dataframe without a filename column
    """
    df = df.drop(['Filename'], axis=1)
    return df


def add_filename_column_to_single_df(df, filename):
    """
    Function: Takes a dataframe and adds a filename column. It populates each element with the variable 'filename'.
    :param df: Dataframe passed in
    :param filename: name of the file
    :return: dataframe with filename column
    """
    length = len(df)
    filenameList = [filename]*length
    df['Filename'] = filenameList
    return df


def sort_values(args, df):
    """
    Function: Sorts values based on sample name column
    :param df: Unsorted dataframe
    :return: Sorted dataframe
    """
    if df.empty:
        return df
    return df.sort_values([args.key]).reset_index(drop=True)




def guess_file_type(filename):
    """
    :param filename: name of the file
    :return: the file handle that presumably tells the type of the file
    """
    return os.path.splitext(filename)[1].strip('.')


def create_directory(folderName):
    try:
        os.mkdir(folderName)
    except FileExistsError:
        raise FileExistsError(f"Folder named '{folderName}' already exists. Specify a different output name.")


def join_two_dataframes(lhs, rhs):
    """
    :param lhs: dataframe one
    :param rhs: second dataframe
    :return: concatenated dataframe
    """
    return pd.concat([lhs, rhs], sort=False, ignore_index=True)


def check_two_dfs_for_merge_conflict(args, leftDataframe, rightDataframe, sheetname):
    df = join_two_dataframes(leftDataframe, rightDataframe)
    duplicates = find_duplicate_sample_names(args, df)
    for name in duplicates:
        temp = df[df[args.key] == name]
        for column in temp.loc[:, temp.columns != 'Filename']:
            # This for loop iterates through each of the columns in the temporary dataframe to check how many
            # unique entries are in each. If the answer is more than one, it calls the 'make_user_choose_two_files'
            # function.
            instances = temp[column].nunique()
            if instances > 1:
                # The above if statement checks if there is more than one unique value per column. If the global default
                # variable is (None), then it prompts the user to choose which value to accept. Then, it changes the
                # values in each dataframe to match this.
                if args.interactive:
                    merger = InteractiveActions()
                    df.at[df[args.key] == name, column] = merger(temp['Filename'].values[0],
                                                                                 temp['Filename'].values[1],
                                                                                 sheetname,
                                                                                 temp[args.key].values[0],
                                                                                 column,
                                                                                 temp[column].values[0],
                                                                                 temp[column].values[1])
                else:
                    merger = args.mergedefault
                    df.at[df[args.key] == name, column] = merger(temp[column].values[0],
                                                                 temp[column].values[1])
    return df


def find_duplicate_sample_names(args, df):
    if df.empty:
        return []
    else:
        column = args.key
        # Selects the column we want to search
        duplicated_names = df[[column]].duplicated(keep='last')
        # Goes through the column and identifies whether or not each name has been repeated. If we had:
        #
        #   Sample Name
        # 0 foo
        # 1 bar
        # 2 foo
        #
        # duplicated_names would be
        #
        #   Sample Name
        # 0 False
        # 1 False
        # 2 True
        #
        # The 'keep=last' ensures that we aren't counting repeated sample names twice.
        return list(df[column][duplicated_names].drop_duplicates())
        # This creates a new dataframe of the sample name column with only the values that are duplicated, then
        # turns it into a list. It drops any duplicates.


def check_for_sample_name_completeness(args, df, filename, sheetname, ftype):
    """
    Function: Checks the first column for empty cells. If there is an empty cell, throw an error. Otherwise, return
    the original dataframe

    For whatever reason, the error isn't thrown when I include the try and except statements, that's why I commented
    them out

    :param df: dataframe to check
    :param filename: name of the file
    :param sheetname: name of the sheet
    :param column: name of the column that you are checking
    :return: dataframe with all entries in the 'column' filled. If there is an empty one, an error is thrown.
    """
    #try:
    for i in range(len(df)):
        if pd.isna(list(df[args.key])[i]) is True:
            raise IOError(f"Empty cell in sample name in row {i + 1} in file {filename} in sheet {sheetname}")
    return df
    #except IOError:
    #    IOError(f"Empty cell in sample name in row {i + 1} in file {filename} in sheet {sheetname}")


def check_for_sample_name_uniqueness(args, df, filename, sheetname, ftype):
    """
    Functionality: Makes sure there are no repeated sample names, similar to the 'check_for_merge_conflict' function
    :param df: dataframe to check
    :param filename: name of the file
    :param sheetname: name of the sheet
    :param column: column that is being checked
    :return: fixed dataframe
    """
    duplicates = find_duplicate_sample_names(args, df)
    for name in duplicates:
        temp = df[df[args.key] == name]
        for column in temp:
            instances = temp[column].nunique()
            if instances > 1:
                raise ValueError(f"Aborting due to conflict in file '{filename}' in sheet '{sheetname}'")
    return fix_dataframe(args, df)


def check_sample_name_is_represented_in_dataframe(args, df, filename, sheetname, ftype):
    sampleName = args.key
    if sampleName not in df.columns:
        errorMessage = (f"The sample name '{sampleName}' is not a column name in file '{filename}' "
                        f"within sheet '{sheetname}'." if ftype == 'xlsx' else '.')
        raise KeyError(errorMessage)
    return df


def check_if_nan(df):
    """
    This finds the non-NaN value. If all the values are NaN, it just returns NaN.
    :param df: column in the dataframe that is being checked
    :return: Either np.NaN or the location of the non-NaN value
    """
    df = df[~pd.isna(df)]
    # This creates a new dataframe where the only values are not
    if len(df) > 0:
        return df.iloc[0]
    else:
        return np.NaN


def combiner(args, df):
    """
    Function: Takes a dataframe with several different rows, but in each column there is no more than
    1 non-NaN value. It substitues all NaN values with this value, if possible, otherwise it leaves it as
    'NaN'.
    :param df: dataframe being combined
    :return: corrected dataframe
    """
    df_valid = df.groupby(by=args.key).agg(dict.fromkeys(df.columns[0:], check_if_nan))
    return df_valid


def fix_dataframe(args, df):
    """
    Function: Takes a dataframe with several identical sample name entries and fixes it, merging rows were applicable.
    Here's how it works. It goes through the first column of the dataframe and creates an array of all the repeated
    sample names. Then, for each repeated name, it creates a temporary dataframe with the repeated rows and merges the
    rows together. It favors non-NaN values when populating the cells, but if both values are NaN, it leaves it as NaN.
    Then, it deletes all the repeated rows in the original dataframe and sticks the new, merged row onto the bottom.

    :param df: dataframe to be fixed
    :return: dataframe without diplicated sample name entries
    """
    if df.empty:
        return df
    combined = create_empty_df()
    duplicates = find_duplicate_sample_names(args, df)
    # creates an array of all the repeated sample names
    for repeatedName in duplicates:
        temp = df[df[args.key] == repeatedName]
        # creates a temporary dataframe with only the rows with the repeated name
        combined = join_two_dataframes(combined, combiner(args, temp))
        # There might be several different repeated names. There will be one row for each fixed name, so 'combined'
        # will contain each of these rows. 'Combiner' will be the function that merges the rows.
    dfWithoutDuplicates = df.drop_duplicates(subset=[args.key], keep=False)
    # Deletes all repeated rows from the original dataframe
    return join_two_dataframes(dfWithoutDuplicates, combined)


def take_keyword(input, values):
    """
    Function: This takes a number between 1 and 5 and outputs the corresponding value of the array, or aborts the
    merge if that is what the user chooses.
    :param argument: keyboard entry from the user
    :param values: list of the possible valuse for the user to chose
    :return: value chosen by the user
    """
    action = {
        1: values[0],
        # value from file 1
        2: values[1],
        # value from file 2
        3: str(list(values)),
        # list of both of them
        4: (values[0]+values[1])/2,
        # take average of values
        5: 'exit',
        # abort merge
    }
    if action.get(input) is 'exit':
        raise ValueError('Aborting merge due to merge conflict')
    selectedIndex = action.get(input, "Invalid selection. Aborting merge.")
    return selectedIndex


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


def setup_validator():
    """
    Function: This sets up a validator. What this does is checks to make sure each file won't conflict against itself.

    The way a validator works is by gathering a few functions that test the dataframe for a certain condition. It will
    either fix the problem if possible, or throw an error. The two functions we have here will check to make sure there
    are no repeated sample names, and that there are no blank sample names.

    The check_for_sample_name_completeness is
    first. It will take in a dataframe as a parameter and go through the first column. If there are any empty spaces,
    it presents an error to the user. There is no way to fix this problem unless the user goes an manually adds it to
    the file. If no blank spaces are found, it will return the dataframe it started with and this will be passed to the
    next function.

    Next is the check_for_sample_name_uniqueness. This makes sure there aren't any repeated names in the file. If it
    does find a repeated value, it tries to fix it by first checking each cell for conflicting values. If none are
    found, it smushes the offending rows together into one. Then, it returns the corrected dataframe.

    With these, all we have to do is df = validate(df) and it'll make sure the incoming dataframe is good.

    :return: an instance of the validator that contains functions to make sure the dataframe won't throw any merge
    conflicts.
    """
    validate = QMDataFrameValidator()
    validate.add_callback(check_sample_name_is_represented_in_dataframe)
    validate.add_callback(check_for_sample_name_completeness)
    validate.add_callback(check_for_sample_name_uniqueness)
    return validate


def create_empty_df(header=None):
    """
    Function: Pretty self explanitory. Just creates an empty dataframe with no rows or columns. We can specify
    header values by giving it an array, such as create_empty_df(['header1', 'header2', 'header3'])
    :param header: an array of all the column names we want
    :return: an empty dataframe
    """
    return pd.DataFrame(columns=header)


def get_dataframe(args, filename, ftype, sheetname):
    validate = setup_validator()
    # Look under the setup_validator function, I explain how the validator works.
    df = read(filename, ftype, sheetname).as_dataframe()
    if not df.empty:
        df = validate(args, df, filename, sheetname, ftype)
    return df


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    if isinstance(args, list):
        args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug(f"Starting confluence-merge.")
    try:
        execute(args)
    except Exception as e:
        _logger.error(f"Unhandled exception raised message: {e}")
        if isinstance(args, list):
            sys.exit(1)
        else:
            raise e
    _logger.debug(f"Completed confluence-merge.")


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()