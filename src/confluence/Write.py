from .io.excel import ExcelWriter
from .io.text import TextWriter
from .io.JSON import JSONWriter
from .io.CSV import CSVWriter
from .io.pif import PifWriter
from .merge import merge_dataframes
import os


def guess_file_type(filename):
    """
    :param filename: name of the file
    :return: the file handle that presumably tells the type of the file
    """
    return os.path.splitext(filename)[1].strip('.')


def get_sheetnames_from_file_df(file_df):
    sheets = list(file_df['sheetname'].drop_duplicates())
    return sheets


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
            'json': write_json,
            'pif': write_pif
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
    sheets = get_sheetnames_from_file_df(file_df)
    for sheet in sheets:
        df_same_sheet = file_df[file_df['sheetname'] == sheet]
        merged_df = merge_dataframes(df_same_sheet, sheet)
        if merged_df.empty:
            writer.write_empty_df(merged_df, sheet)
        else:
            writer.write(merged_df, sheet)
    writer.save_and_close()


def write_text(file_df, outfile, delimiter=' '):
    sheets = get_sheetnames_from_file_df(file_df)
    if len(sheets) == 1:
        writer = TextWriter(outfile, delimiter=delimiter)
        writer.write(merge_dataframes(file_df, sheets[0]))
    else:
        folder = os.path.splitext(outfile)[0]
        create_directory(folder)
        for sheet in sheets:
            modifiedOutfile = folder + '/' + sheet + '_' + outfile
            writer = TextWriter(modifiedOutfile)
            df_same_sheet = file_df[file_df['sheetname'] == sheet]
            merged_df = merge_dataframes(df_same_sheet, sheet)
            writer.write(merged_df)


def write_json(file_df, outfile):
    sheets = get_sheetnames_from_file_df(file_df)
    if len(sheets) == 1:
        writer = JSONWriter(outfile)
        writer.write(merge_dataframes(file_df, sheets[0]))
    else:
        folder = os.path.splitext(outfile)[0]
        create_directory(folder)
        for sheet in sheets:
            modifiedOutfile = folder + '/' + sheet + '_' + outfile
            writer = JSONWriter(modifiedOutfile)
            df_same_sheet = file_df[file_df['sheetname'] == sheet]
            merged_df = merge_dataframes(df_same_sheet, sheet)
            writer.write(merged_df)


def write_csv(file_df, outfile):
    sheets = get_sheetnames_from_file_df(file_df)
    if len(sheets) == 1:
        writer = CSVWriter(outfile)
        writer.write(merge_dataframes(file_df, sheets[0]))
    else:
        folder = os.path.splitext(outfile)[0]
        create_directory(folder)
        for sheet in sheets:
            modifiedOutfile = folder + '/' + sheet + '_' + outfile
            writer = CSVWriter(modifiedOutfile)
            df_same_sheet = file_df[file_df['sheetname'] == sheet]
            merged_df = merge_dataframes(df_same_sheet, sheet)
            writer.write(merged_df)


def write_pif(file_df, outfile):
    sheets = get_sheetnames_from_file_df(file_df)
    if len(sheets) == 1:
        writer = CSVWriter(outfile)
        writer.write(merge_dataframes(file_df, sheets[0]))
    else:
        folder = os.path.splitext(outfile)[0]
        create_directory(folder)
        for sheet in sheets:
            modifiedOutfile = folder + '/' + sheet + '_' + outfile
            writer = PifWriter(modifiedOutfile)
            df_same_sheet = file_df[file_df['sheetname'] == sheet]
            merged_df = merge_dataframes(df_same_sheet, sheet)
            writer.write(merged_df)