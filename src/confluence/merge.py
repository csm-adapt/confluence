import argparse
import pandas as pd
import numpy as np
import os
from excel import ExcelReader
from excel import ExcelWriter
from itertools import product
from validator import QMDataFrameValidator


def merge(dataframes, sheetname):
    """
    TBW
    :param lhs: filename of the left hand file
    :param rhs: filename of the right hand file
    :return:
    """
    keys = list(dataframes.keys())
    values = list(dataframes.values())
    df = join_many_dataframes(values)
    for i, j in product(range(len(keys)), range(len(keys))):
        if j <= i:
            continue
        lhs = keys[i]
        rhs = keys[j]
        left = values[i]
        right = values[j]
        print('comparing: ', lhs, rhs)
        df = merge_conflict(df, join_two_dataframes(left, right), lhs, rhs, sheetname)
    print(df)
    df = fix_dataframe(df)
    return df


def join_two_dataframes(lhs, rhs):
    """
    :param lhs: dataframe one
    :param rhs: second dataframe
    :return: concatenated dataframe
    """
    return pd.concat([lhs, rhs], sort=False, ignore_index=True)


def join_many_dataframes(dfs):
    """
    :param dfs: list of the dataframes
    :return: concatenated dataframe
    """
    temp = pd.DataFrame()
    for df in dfs:
        temp = pd.concat([temp, df], sort=False, ignore_index=True)
    return temp


def merge_conflict(bigdf, df, lhs, rhs, sheetname, column='Sample Name'):
    """
    :param bigdf: Concatenated dataframe of all the files being entered
    :param df: concatenated dataframes of the two files being compared
    :param lhs: file name 1
    :param rhs: file name 2
    :param sheetname: name of the sheet
    :param column: Column of all the sample names
    :return: A version of the big dataframe that is free of
    """
    duplicates = (list(df[column][df[[column]].duplicated(keep='last')].drop_duplicates()))
    for name in duplicates:
        temp = df[df[column] == name]
        for key in temp:
            instances = temp[key].nunique()
            if instances > 1:
                bigdf.at[bigdf[column] == name, key] = make_user_choose_two_files(temp[key].values, temp[key].values[0], temp[key].values[1], lhs, rhs, key, temp[column].values[0], sheetname)
    return bigdf


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


def check_if_nan(df):
    """
    :param df: column in the dataframe that is being checked
    :return: Either np.NaN or the location of the non-NaN value
    """
    df = df[~pd.isna(df)]
    if len(df) > 0:
        print(df.iloc[0])
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


def fix_dataframe(df):
    """
    Function: Takes a dataframe with several identical sample name entries and corrects it. A previous
    function has already made sure there will not be a merge conflict.
    :param df: dataframe to be fixed
    :return: dataframe without diplicated sample name entries
    """
    combined = pd.DataFrame()
    duplicates = (list(df['Sample Name'][df[['Sample Name']].duplicated(keep='last')].drop_duplicates()))
    for name in duplicates:
        temp = df[df['Sample Name'] == name]
        combined = pd.concat([combined, combiner(temp)])
    df = df.drop_duplicates(subset=['Sample Name'], keep=False)
    return join_two_dataframes(df, combined)


def check_for_sample_name_uniqueness(df, filename, sheetname='Sheet 1', column='Sample Name'):
    """
    Functionality: Makes sure there are no repeated sample names
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


def read_excel(filename, sheetname):
    """
    function: reads excel files
    :param filename: file name to be read
    :param sheet: name of the sheet
    :return: reader object for a specific sheet name
    """
    validate = QMDataFrameValidator()
    validate.add_callback(check_for_sample_name_completeness)
    validate.add_callback(check_for_sample_name_uniqueness)
    sheetnames = ExcelReader(filename).sheetnames()
    readers = [ExcelReader(filename, sheetname=sheet) for sheet in sheetnames]
    for reader in readers:
        df = reader.as_dataframe(sheetname)
        validate(df, filename, sheetname)
    sheetReader = ExcelReader(filename, sheetname=sheetname)
    return sheetReader


def make_user_choose_one_file(arr, column, filename='None', sheetname='Sheet 1', sample='None'):
    """
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
            print('Invalid response. Try again.\n')
    return arr[choice-1]


def make_user_choose_two_files(arr, value1, value2, file1, file2, column, sample, sheetname='Sheet1'):
    """
    :param arr: list of conflicting data
    :param value1: first conflicting data point
    :param value2: second conflicting data point
    :param file1: first file
    :param file2: second file
    :param column: column that the conflicting value is from
    :param sample: sample name the conflicting value is from
    :param sheetname: sheet that the values are from
    :return: value that the user choses
    """
    print('Merge conflict between', file1, 'and', file2, 'in sheet', sheetname, 'for sample', sample, 'under column', column,'\n',
          '\n1: Accept value', value1, 'from file', file1,
          '\n2: Accept value', value2, 'from file', file2,
          '\n3: Join files into a list',
          '\n4: Abort the merge\n')
    return switch(int(input('Enter the number\n')), arr)


def switch(argument, values):
    """
    :param argument: keyboard entry from the user
    :param values: list of the possible valuse for the user to chose
    :return: value chosen by the user
    """
    switcher = {
        1: values[0],
        2: values[1],
        3: values,
        4: 'exit',
    }
    if switcher.get(argument) is 'exit':
        exit()
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
    return list(dict.fromkeys(arr))


def excel_parser(files, writer):
    """
    :param files: A dictionary of filenames and their corresponding tile types
    :param writer: An instance of the Excel Writer that can be used to write to the sheet
    :return: none
    """
    sheetnames = get_all_sheetnames(files)
    for sheet in sheetnames:
        arr = []
        for fname, ftype in files.items():
            reader = ExcelReader(fname)
            if sheet in reader.sheetnames():
                arr = np.append(arr, fname)
        dataframes = {fname: read(fname, ftype, sheet).as_dataframe() for fname in arr}
        writer.write_to_sheet(merge(dataframes, sheet), sheet)


def main():
    """
    function: takes arguments from arg parse and puts the files into an excel parser
    :return:
    """
    parser = argparse.ArgumentParser(description='You should know this')
    parser.add_argument('infiles', nargs='+', help='input file')
    parser.add_argument('-o', '--output', help='output file')
    parser.add_argument('-i', '--input', nargs=2, help='file type', action='append')
    args = parser.parse_args()
    outfile = args.output
    files = {infile: None for infile in args.infiles}
    if args.input is not None:
        files.update({infile[1]: infile[0] for infile in args.input})
    writer = ExcelWriter(outfile)
    excel_parser(files, writer)
    writer.save_and_close()


main()



def parse_args(args):
    """Parse command line parameters

    Args:
      args ([str]): command line parameters as list of strings

    Returns:
      :obj:`argparse.Namespace`: command line parameters namespace
    """
    parser = argparse.ArgumentParser(
        description="Just a Fibonnaci demonstration")
    parser.add_argument(
        '--version',
        action='version',
        version='confluence {ver}'.format(ver=__version__))
    parser.add_argument(
        dest="n",
        help="n-th Fibonacci number",
        type=int,
        metavar="INT")
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)
    return parser.parse_args(args)


def setup_logging(loglevel):
    """Setup basic logging

    Args:
      loglevel (int): minimum loglevel for emitting messages
    """
    logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
    logging.basicConfig(level=loglevel, stream=sys.stdout,
                        format=logformat, datefmt="%Y-%m-%d %H:%M:%S")


def main(args):
    """Main entry point allowing external calls

    Args:
      args ([str]): command line parameter list
    """
    args = parse_args(args)
    setup_logging(args.loglevel)
    _logger.debug("Starting crazy calculations...")
    print("The {}-th Fibonacci number is {}".format(args.n, fib(args.n)))
    _logger.info("Script ends here")


def run():
    """Entry point for console_scripts
    """
    main(sys.argv[1:])


if __name__ == "__main__":
    run()
