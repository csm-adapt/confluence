
import sys
import argparse
import pandas as pd
import numpy as np
import os
import inspect
from itertools import product

def run(args):
    """
    Function: This is the function called when the merge.py is used in the terminal.
    :param args: An array of files to be merged
    :return: None
    """
    args = parse_args(args)
    # This creates an arg parser object. It contains all the files, file types, and other information
    # passed from the terminal. For example, if you were to print args.infiles, it would give a list of each
    # file name. If no value is passed for the variable, they return 'False'.
    set_global_variables(args)
    # This sets all the default variables. A user might enter a default action for the program to do in case of a
    # merge conflict (e.g. abort the merge, chose the value from the first file, let the user decide). These variables
    # initialize to 'None' if no default action is specified.
    files = create_df_of_all_infiles(args)
    # This creates a large dataframe containing the file name, the corresponding dataframe, the file type, and the
    # sheetname. This is the object that will be passed to the write function.
    write(files, get_file(args.output, args.outputformat), args.outputformat)
    # This function will write the dataframes to the output file.


def merge(args, sheetname='Sheet1'):
    """
    Function: This does the same thing as 'run()' but instead of writing the dataframes to a file, it returns the
    dataframe.
    :param args:
    :return:
    """
    args = parse_args(args)
    set_global_variables(args)
    files = create_df_of_all_infiles(args)
    files = files[files['sheetname'] == sheetname]
    merged = merge_dataframes(files['filename'], files['dataframe'], sheetname)
    return merged



def merge_dataframes(fnames, dfs, sheetname):
    """
    function: This takes a bunch of different dataframes and merges them into one. It checks for merge conflicts, fixes
    what it can, and returns a single dataframe.
    :param fnames: list of all the filenames
    :param dfs: all the dataframes
    :param sheetname: the sheetname being analyzed
    :return: merged dataframe.
    """
    fnames = list(fnames)
    dfs = list(dfs)
    dfs = compare_each_possible_pair_of_dataframes(fnames, dfs, sheetname)
    # checks each dataframe pair for merge conflicts. It either fixes them or raises an error.
    df = fix_dataframe(join_many_dataframes(dfs))
    # This combines all of them and gets rid of any repeated row
    return df.sort_values([df.columns[0]]).reset_index(drop=True)


def compare_each_possible_pair_of_dataframes(fnames, dfs, sheetname):
    """
    Function: This takes a bunch of dataframes and compares them in pairs of two. If two dataframes are entered,
    it just makes one comparison. If three are entered, it compares 1 and 2, 1 and 3, and 2 and 3. As more and more
    dataframes are entered, the amount of comparisons rises pretty quickly. We might get rid of this function and
    just compare them all at once, but I will keep you posted on that.

    :param fnames: array of file names
    :param dfs: array of dataframes
    :param sheetname: name of the sheet being read
    :return:
    """
    for left, right in product(range(len(fnames)), range(len(fnames))):
        if right <= left:
            continue
        left_filename = fnames[left]
        right_filename = fnames[right]
        left_df = dfs[left]
        right_df = dfs[right]
        dfs[left], dfs[right] = check_for_merge_conflict(left_df, right_df, left_filename, right_filename, sheetname)
    return dfs


def read(filename, ftype=None, sheetname='Sheet1'):
    """
    Function: This is the function we call when we want to read an unknown file. It first takes in the file name
    and file type. If the file type is 'None', it guesses the type based on the file extention. Each file type has an
    accompanying function that contains the reader for that file type (read_excel(), etc.).

    :param filename: name of file
    :param ftype: the type of the file ('xlsx', 'txt', etc)
    :param sheetname: name of the sheet being read. This only applies to .xlsx files
    :return: appropriate file reader
    """
    if ftype is None:
        ftype = guess_file_type(filename)
    try:
        return {
            'xlsx': read_excel(filename, sheetname),
            'txt': read_text(filename),
            'csv': read_csv(filename),
            'json': read_json(filename)
        }[ftype]
    except KeyError:
        raise IOError(f"{ftype} is not a recognized file type.")


def read_excel(filename, sheetname):
    """
    function: reads excel files. This will return an instance of the ExcelReader that you can add '.as_dataframe()' to
    get the file as a dataframe
    :param filename: file name to be read
    :param sheet: name of the sheet
    :return: reader object for a specific sheet name
    """
    reader = ExcelReader(filename, sheetname=sheetname)
    return reader


def read_text(filename):
    """
    Function: reads txt files
    :param filename: Name of the file
    :return: reader object
    """
    reader = TextReader(filename)
    return reader


def read_json(filename):
    """
    Function: Reads JSON files
    :param filename: name of the file
    :return: reader object
    """
    reader = JSONReader(filename)
    return reader


def read_csv(filename):
    """
    Function: reads csv files
    :param filename: file name
    :return: csv reader object
    """
    reader = CSVReader(filename)
    return reader


def write(file_df, outfile, outfiletype):
    """
    Function: This is what writes the dataframes to the target file. It works by first determining what writer to use.
    If no outfiletype is specified, it guesses it based on the file extention. After it chooses the writer to use, it
    passes along the file_df to it.

    :param file_df: dataframe with all the files and their metadata
    :param outfile: output file to write to
    :param outfiletype: type of file
    :return: appropriate reader for writing
    """
    if outfiletype is None:
        outfiletype = guess_file_type(outfile)
    try:
        return {
            'xlsx': write_excel,
            'txt': write_text,
            'csv': write_csv,
            'json': write_json
        }[outfiletype](file_df, outfile)
    except KeyError:
        raise IOError(f"{outfiletype} is not a recognized file type.")


def write_excel(file_df, outfile):
    """
    Function: This is the most complex writer because it is the only one with multiple different sheet names. The way
    it works is by first
    :param files: A dictionary of filenames and their corresponding tile types
    :param outfile: The output file to write to
    :return: none
    """
    writer = ExcelWriter(outfile)
    for sheet in file_df['sheetname'].drop_duplicates():
        df_same_sheet = file_df[file_df['sheetname'] == sheet]
        merged_df = merge_dataframes(df_same_sheet['filename'], df_same_sheet['dataframe'], sheet)
        writer.write(merged_df, sheet)
    writer.save_and_close()


def write_text(files, outfile):
    writer = TextWriter(outfile)
    writer.write(merge_dataframes(files['filename'], files['dataframe'], 'Sheet1'))


def write_json(files, outfile):
    writer = JSONWriter(outfile)
    writer.write(merge_dataframes(files['filename'], files['dataframe'], 'Sheet1'))


def write_csv(files, outfile):
    writer = CSVWriter(outfile)
    writer.write(merge_dataframes(files['filename'], files['dataframe'], 'Sheet1'))


def join_two_dataframes(lhs, rhs):
    """
    :param lhs: dataframe one
    :param rhs: second dataframe
    :return: concatenated dataframe
    """
    return pd.concat([lhs, rhs], sort=False, ignore_index=True)


def join_many_dataframes(dataframes):
    """
    :param dfs: list of the dataframes
    :return: concatenated dataframe
    """
    combined = create_empty_df()
    for df in dataframes:
        combined = pd.concat([combined, df], sort=False, ignore_index=True)
    return combined


def guess_file_type(filename):
    """
    :param filename: name of the file
    :return: the file handle that presumably tells the type of the file
    """
    print(filename)
    return os.path.splitext(filename)[1].strip('.')


def check_for_merge_conflict(left_df, right_df, left_filename, right_filename, sheetname):
    """
    :param left: left dataframe
    :param right: right dataframe
    :param lhs: file name 1
    :param rhs: file name 2
    :param sheetname: name of the sheet
    :param column: Column of all the sample names
    :return: A version of the big dataframe that is free of merge conflicts
    """
    df = join_two_dataframes(left_df, right_df)
    # duplicates = (list(df[df.columns[0]][df[[df.columns[0]]].duplicated(keep='last')].drop_duplicates()))
    duplicates = find_duplicate_sample_names(df)
    # Creates a list of all the duplicate sample names found, regardless of if they will eventually
    # cause a merge conflict
    for name in duplicates:
        temp = df[df[df.columns[0]] == name]
        # creates a temporary dataframe of all the rows with duplicate sample names
        for key in temp:
            # This for loop iterates through each of the columns in the temporary dataframe to check how many
            # unique entries are in each. If the answer is more than one, it calls the 'make_user_choose_two_files'
            # function.
            instances = temp[key].nunique()
            if instances > 1:
                # The above if statement checks if there is more than one unique value per column. If the global default
                # variable is (None), then it prompts the user to choose which value to accept. Then, it changes the
                # values in each dataframe to match this.
                choice = make_user_choose_between_two_files(temp[key].values, left_filename, right_filename, key,
                                                            temp[df.columns[0]].values[0], sheetname)
                right_df.at[right_df[df.columns[0]] == name, key] = choice
                left_df.at[left_df[df.columns[0]] == name, key] = choice
    return [fix_dataframe(left_df), fix_dataframe(right_df)]


def find_duplicate_sample_names(df):
    column = df.columns[0]
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


def check_for_sample_name_completeness(df, filename, sheetname='Sheet1'):
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
        # print(list(df[df.columns[0]])[i])
        if pd.isna(list(df[df.columns[0]])[i]) is True:
            raise IOError(f"Empty cell in sample name in row {i + 1} in file {filename} in sheet {sheetname}")
    return df
    #except IOError:
    #    IOError(f"Empty cell in sample name in row {i + 1} in file {filename} in sheet {sheetname}")


def check_for_sample_name_uniqueness(df, filename, sheetname='Sheet1'):
    """
    Functionality: Makes sure there are no repeated sample names, similar to the 'check_for_merge_conflict' function
    :param df: dataframe to check
    :param filename: name of the file
    :param sheetname: name of the sheet
    :param column: column that is being checked
    :return: fixed dataframe
    """
    # duplicates = (list(df[df.columns[0]][df[[df.columns[0]]].duplicated(keep='last')].drop_duplicates()))
    duplicates = find_duplicate_sample_names(df)
    for name in duplicates:
        temp = df[df[df.columns[0]] == name]
        for key in temp:
            instances = temp[key].nunique()
            if instances > 1:
                df.loc[df[df.columns[0]] == name, key] = make_user_choose_within_one_file(temp[key].values, key, filename, sheetname, temp[df.columns[0]].values[0])
    return fix_dataframe(df)


def make_user_choose_within_one_file(arr, column, filename='None', sheetname='Sheet1', sample='None'):
    """
    Function: this is called when the user is prompted to resolve a merge conflict in a single file.
    It presents the values that are conflicting with each other and has the user enter the number of
    the value of his/her choice.
    :param arr: list of the sample names that are causing a conflict
    :param column: column with the conflicting values
    :param filename: name of the file the dataframe came from
    :param sheetname: name of the sheet
    :param sample: sample name with conflicting values
    :return: returns the value that the user picks
    """
    print('Multiple values found in', filename, 'in sheet', sheetname, 'for sample', sample, 'under column', column)
    while True:
        for i in range(len(arr)):
            print(i+1, ':', arr[i])
        choice = int(input('Enter number of value\n'))
        if (choice-1) in range(0, len(arr)):
            break
        else:
            print('Invalid response. Must enter a number between 1 and', len(arr), 'Try again.\n')
    return arr[choice-1]


def make_user_choose_between_two_files(arr, file1, file2, column, sample, sheetname='Sheet1'):
    """
    function: this is called when two files are conflicting. It displays each value and its corresponding
    sheet name and file name, then asks the user to input their choice. Also, it gives the option of aborting the
    code or entering the files in as a list.

    :param arr: list of conflicting data
    :param file1: first file name
    :param file2: second file name
    :param column: column that the conflicting value is from
    :param sample: sample name the conflicting value is from
    :param sheetname: sheet that the values are from
    :return: numerical value that the user chooses
    """
    if default is not None:
        return take_keyword(convert_merge_default_into_number(default), arr)
    else:
        print('Merge conflict between', file1, 'and', file2, 'in sheet',
              sheetname, 'for sample', sample, 'under column', column, '\n',
              '\n1: Accept value', arr[0], 'from file', file1,
              '\n2: Accept value', arr[1], 'from file', file2,
              '\n3: Join files into a list',
              '\n4: Take average (mean)',
              '\n5: Abort the merge\n')
        return take_keyword(int(input('Enter the number\n')), arr)


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


def combiner(df):
    """
    Function: Takes a dataframe with several different rows, but in each column there is no more than
    1 non-NaN value. It substitues all NaN values with this value, if possible, otherwise it leaves it as
    'NaN'.
    :param df: dataframe being combined
    :return: corrected dataframe
    """
    df_valid = df.groupby(by=df.columns[0]).agg(dict.fromkeys(df.columns[0:], check_if_nan))
    return df_valid


def fix_dataframe(df):
    """
    Function: Takes a dataframe with several identical sample name entries and fixes it, merging rows were applicable.
    Here's how it works. It goes through the first column of the dataframe and creates an array of all the repeated
    sample names. Then, for each repeated name, it creates a temporary dataframe with the repeated rows and merges the
    rows together. It favors non-NaN values when populating the cells, but if both values are NaN, it leaves it as NaN.
    Then, it deletes all the repeated rows in the original dataframe and sticks the new, merged row onto the bottom.

    :param df: dataframe to be fixed
    :return: dataframe without diplicated sample name entries
    """
    combined = create_empty_df()
    duplicates = find_duplicate_sample_names(df)
    # creates an array of all the repeated sample names
    for repeatedName in duplicates:
        temp = df[df[df.columns[0]] == repeatedName]
        # creates a temporary dataframe with only the rows with the repeated name
        combined = join_two_dataframes(combined, combiner(temp))
        # There might be several different repeated names. There will be one row for each fixed name, so 'combined'
        # will contain each of these rows. 'Combiner' will be the function that merges the rows.
    dfWithoutDuplicates = df.drop_duplicates(subset=[df.columns[0]], keep=False)
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
    return action.get(input, "Invalid selection. Aborting merge.")


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


def convert_merge_default_into_number(input):
    """
    Function: The merge default is entered as a string, and this converts it to a number. This function also catches
    if the user enters an invalid merge action.
    :param input: merge default action passed in by the user
    :return: value from 1 to 4 to give to the merge_conflict function should a conflict arise
    """
    try:
        return{
            'first': 1,
            'second': 2,
            'join': 3,
            'average': 4,
            'abort': 5
        }[input]
    except KeyError:
        raise KeyError(f"{input} is not a recognized default action")


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
    df_rows_from_args_input = [file_df_row(file, ftype) for file, ftype in args.input] if args.input else []
    files = join_many_dataframes(df_rows_from_args_input + df_rows_from_args_infile)
    return files


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
    validate = setup_validator()
    file_df = create_empty_df(['filename', 'dataframe', 'type', 'sheetname'])
    sheets = get_sheetnames(filename) if ftype == 'xlsx' else [txtSheetname]
    # if the file type is xlsx, get all the sheetnames as a list. Otherwise, it sets the sheetname as the txtSheetname
    # variable, which is a global variable set by the user. If the user does not specify a sheetname for non-excel
    # files, it defaults to 'Sheet1'.
    for sheetname in sheets:
        df = read(filename, ftype, sheetname).as_dataframe()
        # This is where we finally get to read the dataframe for the file. The read() function determines what reader
        # to use, and returns the file as a dataframe.
        df = validate(df, filename, sheetname)
        # Look under the setup_validator function, I explain how the validator works.
        file_df = add_row_to_file_df(file_df, filename, df, ftype, sheetname)
    # Some files have multiple sheetnames and will therefore have multiple rows in the file dataframe. This adds a new
    # row for each sheet.
    return file_df


def find_default_action(args):
    """
    Function: There's a few actions the user can set up as a default in case of a merge conflice. These are 'quiet',
    'first', 'second', 'abort', 'join', and 'interactive'. If no option is specified, default is 'abort'
    :param args: the argparser
    :return: default merge action
    """
    default = args.mergedefault if args.mergedefault is not None else 'abort'
    # If the user has set a default action, set 'default' to that action. Otherwise, set 'default' to 'abort'
    default = 'abort' if args.quiet else default
    # The user can specify '-q' which means quiet. If this is the case, set the default value to 'abort'
    default = None if args.interactive else default
    # If the user specifies '--interactive', set default to None.
    return default


def parse_args(args):
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
    return parser.parse_args(args)


def set_global_variables(args):
    """
    Function: initialize the global variables. As of now, there are two, but I might add more later.
    :param args:
    :return: None
    """
    global default
    global txtSheetname
    default = find_default_action(args)
    txtSheetname = args.sheetname if args.sheetname else 'Sheet1'
    # This gives the user an option to specify a sheetname for non-excel files, otherwise the default name is 'Sheet1'


if __name__ == "__main__":
    from excel import ExcelReader
    from excel import ExcelWriter
    from text import TextReader
    from text import TextWriter
    from JSON import JSONReader
    from JSON import JSONWriter
    from CSV import CSVReader
    from CSV import CSVWriter
    from validator import QMDataFrameValidator
    run(sys.argv[1:])
else:
    from .excel import ExcelReader
    from .excel import ExcelWriter
    from .text import TextReader
    from .text import TextWriter
    from .JSON import JSONReader
    from .JSON import JSONWriter
    from .CSV import CSVReader
    from .CSV import CSVWriter
    from .validator import QMDataFrameValidator
