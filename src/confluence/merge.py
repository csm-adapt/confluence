import argparse
import pandas as pd
import numpy as np
import os
from excel import ExcelReader #These are underlined red, indicating an error, however no error is thrown if
                                #the code is run.
from excel import ExcelWriter
from itertools import product
from validator import QMDataFrameValidator #imports the validator


def merge(dataframes, sheetname):
    """
    Function: compare each of the dataframes and check for conflicts, then return a fixed dataframe
    :param lhs: filename of the left hand file
    :param rhs: filename of the right hand file
    :return:
    """
    fnames = list(dataframes.keys())
    dfs = list(dataframes.values())
    join_many_dataframes(dfs)
    for i, j in product(range(len(fnames)), range(len(fnames))):
        if j <= i:
            continue
        lhs = fnames[i]
        rhs = fnames[j]
        left = dfs[i]
        right = dfs[j]
        dfs[i], dfs[j] = merge_conflict(left, right, lhs, rhs, sheetname) #Checks for merge conflict
    return fix_dataframe(join_many_dataframes(dfs))


def merge_conflict(left, right, lhs, rhs, sheetname, column='Sample Name'):
    """
    :param bigdf: Concatenated dataframe of all the files being entered
    :param smalldf: smaller concatenated dataframes of the two files being compared
    :param lhs: file name 1
    :param rhs: file name 2
    :param sheetname: name of the sheet
    :param column: Column of all the sample names
    :return: A version of the big dataframe that is free of merge conflicts
    """
    df = join_two_dataframes(left, right)
    duplicates = (list(df[column][df[[column]].duplicated(keep='last')].drop_duplicates()))
    # Creates a list of all the duplicate sample names found, regardless of if they will eventually
    # cause a merge conflict
    for name in duplicates:
        temp = df[df[column] == name]
        # creates a temporary dataframe of all the rows with duplicate sample names
        for key in temp:
            # This for loop iterates through each of the columns in the temporary dataframe to check how many
            # unique entries are in each. If the answer is more than one, it calls the 'make_user_choose_two_files'
            # function.
            instances = temp[key].nunique()
            if instances > 1:
                choice = make_user_choose_two_files(temp[key].values, lhs, rhs, key, temp[column].values[0], sheetname)
                right.at[right[column] == name, key] = choice
                left.at[left[column] == name, key] = choice
                # The above if statement checks if there is more than one unique value per column. If the global default
                # variable is (None), then it prompts the user to choose which value to accept. Then, it changes the
                # values in each dataframe to match this.
    return [fix_dataframe(left), fix_dataframe(right)]


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
    combined = pd.DataFrame()
    for df in dataframes:
        combined = pd.concat([combined, df], sort=False, ignore_index=True)
    return combined


def guess_file_type(filename):
    """
    :param filename: name of the file
    :return: the file handle that presumably tells the type of the file
    """
    return os.path.splitext(filename)[1].strip('.')


def read(filename, ftype, sheetname):
    """
    :param filename: name of file
    :param ftype: the type of the file ('xlsx', 'txt', etc)
    :param sheetname: name of the sheet being read
    :return: appropriate file reader
    """
    if ftype is None:
        ftype = guess_file_type(filename)
    try:
        return {
            'xlsx': read_excel,
            #'txt': read_text,
            #'csv': read_csv,
            #'json': read_json
        }[ftype](filename, sheetname)
    except KeyError:
        raise IOError(f"{ftype} is not a recognized file type.")


def write(files, filename, ftype):
    """
    :param filename: name of file
    :param ftype: the type of the file ('xlsx', 'txt', etc)
    :param sheetname: name of the sheet being read
    :return: appropriate file reader
    """
    if ftype is None:
        ftype = guess_file_type(filename)
    try:
        return {
            'xlsx': write_excel,
            #'txt': write_text,
            #'csv': write_csv,
            #'json': write_json
        }[ftype](files, filename)
    except KeyError:
        raise IOError(f"{ftype} is not a recognized file type.")


def check_for_sample_name_completeness(df, filename, sheetname='Sheet 1', column='Sample Name'):
    """
    :param df: dataframe to check
    :param filename: name of the file
    :param sheetname: name of the sheet
    :param column: name of the column that you are checking
    :return: dataframe with all entries in the 'column' filled. If there is an empty one, an error is thrown.
    """
    try:
        for i in range(len(df)):
            if pd.isna(list(df[column])[i]) is True:
                raise IOError
        return df
    except IOError:
        IOError(f"Empty cell in sample name in row {i + 1} in file {filename} in sheet {sheetname}")


def check_for_sample_name_uniqueness(df, filename, sheetname='Sheet 1', column='Sample Name'):
    """
    Functionality: Makes sure there are no repeated sample names, similar to the 'merge_conflict' function
    :param df: dataframe to check
    :param filename: name of the file
    :param sheetname: name of the sheet
    :param column: column that is being checked
    :return: fixed dataframe
    """
    duplicates = (list(df[column][df[[column]].duplicated(keep='last')].drop_duplicates()))
    for name in duplicates:
        temp = df[df[column] == name]
        for key in temp:
            instances = temp[key].nunique()
            if instances > 1:
                df.loc[df[column] == name, key] = make_user_choose_one_file(temp[key].values, key, filename, sheetname, temp[column].values[0])
    return fix_dataframe(df)


def check_files_are_represented_in_dataframe(self):
    pass


def check_if_nan(df):
    """
    :param df: column in the dataframe that is being checked
    :return: Either np.NaN or the location of the non-NaN value
    """
    df = df[~pd.isna(df)]
    if len(df) > 0:
        return df.iloc[0]
    else:
        return np.NaN


def combiner(df):
    """
    Function: Takes a dataframe with several different rows, but in each column there is no more than
    1 non-NaN value. It substitues all NaN values with data, if possible, otherwise it leaves it as
    'NaN'.
    :param df: dataframe being combined
    :return: corrected dataframe
    """
    df_valid = df.groupby(by='Sample Name').agg(dict.fromkeys(df.columns[0:], check_if_nan))
    return df_valid


def fix_dataframe(df, column='Sample Name'):
    """
    Function: Takes a dataframe with several identical sample name entries and corrects it. A previous
    function has already made sure there will not be a merge conflict.
    :param df: dataframe to be fixed
    :return: dataframe without diplicated sample name entries
    """
    combined = pd.DataFrame()
    duplicates = (list(df[column][df[[column]].duplicated(keep='last')].drop_duplicates()))
    for name in duplicates:
        temp = df[df[column] == name]
        combined = pd.concat([combined, combiner(temp)])
    df = df.drop_duplicates(subset=[column], keep=False)
    return join_two_dataframes(df, combined)


# def read_excel(filename, sheetname):
#     """
#     function: reads excel files
#     :param filename: file name to be read
#     :param sheet: name of the sheet
#     :return: reader object for a specific sheet name
#     """
#
#     sheetnames = ExcelReader(filename).sheetnames()
#     readers = [ExcelReader(filename, sheetname=sheet) for sheet in sheetnames]
#     for reader in readers:
#         df = reader.as_dataframe(sheetname)
#     sheetReader = ExcelReader(filename, sheetname=sheetname)
#     return sheetReader


def read_excel(filename, sheetname):
    """
    function: reads excel files
    :param filename: file name to be read
    :param sheet: name of the sheet
    :return: reader object for a specific sheet name
    """

    reader = ExcelReader(filename, sheetname=sheetname)
    return reader


def make_user_choose_one_file(arr, column, filename='None', sheetname='Sheet1', sample='None'):
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
    print('Multiple values found in', filename, 'in sheet', sheetname,'for sample', sample, 'under column', column)
    while True:
        for i in range(len(arr)):
            print(i+1, ':', arr[i])
        choice = int(input('Enter number of value\n'))
        if (choice-1) in range(0, len(arr)):
            break
        else:
            print('Invalid response. Must enter a number between 1 and', len(arr), 'Try again.\n')
    return arr[choice-1]


def make_user_choose_two_files(arr, file1, file2, column, sample, sheetname='Sheet1'):
    """
    function: this is called when two files are conflicting. It displays each value and its corresponding
    sheet name and file name, then asks the user to input their choice. Also, it gives the option of aborting the
    code or entering the files in as a list.
    :param arr: list of conflicting data
    :param value1: first conflicting data point
    :param value2: second conflicting data point
    :param file1: first file name
    :param file2: second file name
    :param column: column that the conflicting value is from
    :param sample: sample name the conflicting value is from
    :param sheetname: sheet that the values are from
    :return: value that the user choses
    """
    if default is not None:
        return switch(convert_merge_default(default), arr)
    else:
        print('Merge conflict between', file1, 'and', file2, 'in sheet', sheetname, 'for sample', sample, 'under column', column,'\n',
              '\n1: Accept value', arr[0], 'from file', file1,
              '\n2: Accept value', arr[1], 'from file', file2,
              '\n3: Join files into a list',
              '\n4: Abort the merge\n')
        return switch(int(input('Enter the number\n')), arr)


def switch(argument, values):
    """
    Function: This takes a number between 1 and 4 and outputs the corresponding value of the array, or aborts the
    function if that is what the user chooses.
    :param argument: keyboard entry from the user
    :param values: list of the possible valuse for the user to chose
    :return: value chosen by the user
    """
    switcher = {
        1: values[0],
        2: values[1],
        3: str(list(values)),
        4: 'exit',
    }
    if switcher.get(argument) is 'exit':
        raise ValueError('Aborting merge due to merge conflict')
    return switcher.get(argument, "Invalid selection")


def get_all_sheetnames(files):
    """
    :param files: all the files being accessed
    :return: a list of every sheet name that is being used
    """
    arr = []
    for file in files:
        reader = ExcelReader(file)
        arr = np.append(arr, reader.sheetnames())
    return list(dict.fromkeys(arr))#Eliminates duplicate names while still preserving order


def write_excel(files, outfile):
    """
    Function: takes all the input excel files and outputs them to one single file
    :param files: A dictionary of filenames and their corresponding tile types
    :param outfile: The output file to write to
    :return: none
    """
    writer = ExcelWriter(outfile)
    validate = QMDataFrameValidator()
    validate.add_callback(check_for_sample_name_completeness)
    validate.add_callback(check_for_sample_name_uniqueness)
    sheetnames = get_all_sheetnames(files)
    for sheet in sheetnames:
        temp = {}
        for fname, ftype in files.items():
            reader = ExcelReader(fname)
            if sheet in reader.sheetnames():
                temp.update({fname: ftype})
        dataframes = {fname: validate(read(fname, ftype, sheet).as_dataframe(), fname, sheet) for fname, ftype in temp.items()}
        writer.write_to_sheet(merge(dataframes, sheet), sheet)
    writer.save_and_close()


def convert_merge_default(input):
    """
    :param input: arg passed into the merge default by the user
    :return: value from 1 to 4 to give to the merge_conflict function should a conflict arise
    """
    return{
        'first': 1,
        'second': 2,
        'join': 3,
        'abort': 4
    }[input]


def get_file(fname, ftype):
    if ftype is None:
        ftype = guess_file_type(fname)
    return os.path.join(os.path.splitext(fname)[0] + "." + ftype.strip('.'))


def parse_args():
    """
    function: return a parser with all the args the user passes to the function
    :return: parser containing all the args
    """
    parser = argparse.ArgumentParser(description='parse arguments')
    parser.add_argument('infiles', nargs='+', help='input file')
    parser.add_argument('-o', '--output', help='output file')
    parser.add_argument('-i', '--input', nargs=2, help='file type', action='append')
    parser.add_argument('-m', '--mergedefault', help='default solution to merges')
    parser.add_argument('--interactive', action='store_true', help='make the program prompt user for input in case of conflict')
    parser.add_argument('--outputformat', help='specify output format')
    parser.add_argument('-q', '--quiet', action='store_true', help='Should a merge conflict happen, default to abort')
    return parser.parse_args()


def main():
    """
    function: takes arguments from arg parse and puts the files into an excel parser
    :return:
    """
    global default
    args = parse_args()
    files = {infile: None for infile in args.infiles}
    default = 'abort' if args.quiet else None
    default = args.mergedefault if args.mergedefault is not None else 'abort'
    default = None if args.interactive else default
    if args.input is not None:
        files.update({get_file(infile[1], infile[0]): infile[0] for infile in args.input})
    write(files, filename=get_file(args.output, args.outputformat), ftype=args.outputformat)


main()




# def parse_args(args):
#     """Parse command line parameters
#
#     Args:
#       args ([str]): command line parameters as list of strings
#
#     Returns:
#       :obj:`argparse.Namespace`: command line parameters namespace
#     """
#     parser = argparse.ArgumentParser(
#         description="Just a Fibonnaci demonstration")
#     parser.add_argument(
#         '--version',
#         action='version',
#         version='confluence {ver}'.format(ver=__version__))
#     parser.add_argument(
#         dest="n",
#         help="n-th Fibonacci number",
#         type=int,
#         metavar="INT")
#     parser.add_argument(
#         '-v',
#         '--verbose',
#         dest="loglevel",
#         help="set loglevel to INFO",
#         action='store_const',
#         const=logging.INFO)
#     parser.add_argument(
#         '-vv',
#         '--very-verbose',
#         dest="loglevel",
#         help="set loglevel to DEBUG",
#         action='store_const',
#         const=logging.DEBUG)
#     return parser.parse_args(args)
#
#
# def setup_logging(loglevel):
#     """Setup basic logging
#
#     Args:
#       loglevel (int): minimum loglevel for emitting messages
#     """
#     logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
#     logging.basicConfig(level=loglevel, stream=sys.stdout,
#                         format=logformat, datefmt="%Y-%m-%d %H:%M:%S")
#
#
# def main(args):
#     """Main entry point allowing external calls
#
#     Args:
#       args ([str]): command line parameter list
#     """
#     args = parse_args(args)
#     setup_logging(args.loglevel)
#     _logger.debug("Starting crazy calculations...")
#     print("The {}-th Fibonacci number is {}".format(args.n, fib(args.n)))
#     _logger.info("Script ends here")
#
#
# def run():
#     """Entry point for console_scripts
#     """
#     main(sys.argv[1:])
#
#
# if __name__ == "__main__":
#     run()
