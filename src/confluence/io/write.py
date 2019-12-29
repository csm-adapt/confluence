import os
from .excel import ExcelWriter
from .text import TextWriter
from .JSON import JSONWriter
from .CSV import CSVWriter
from .pif import PifWriter

def guess_file_type(filename):
    """
    :param filename: name of the file
    :return: the file handle that presumably tells the type of the file
    """
    return os.path.splitext(filename)[1].strip('.')


def write(metadatalist, outfile, outfiletype):
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
        }[outfiletype](metadatalist, outfile)
    except KeyError:
        raise IOError(f"{outfiletype} is not a recognized file type.")


def write_excel(metadatalist, outfile):
    """
    Function: This is the most complex writer because it is the only one with multiple different sheet names. The way
    it works is by first getting all the sheetnames that will have to be written to. Then, for each sheetname, it grabs
    the dataframes in the file dataframe with said sheetname, merges them, then writes to the file. After all sheetnames
    are satisfied, it saves and closes the file.
    :param files: A dictionary of filenames and their corresponding tile types
    :param outfile: The output file to write to
    :return: none
    """
    writer = ExcelWriter(outfile)
    for metadata in metadatalist:
        if metadata.dataframe.empty:
            writer.write_empty_df(metadata.dataframe, metadata.sheetname)
        else:
            writer.write(metadata.dataframe, metadata.sheetname)
    writer.save_and_close()


def write_text(metadatalist, outfile, delimiter=' '):
    """
    Function: Writes the dataframe to a text file. If multiple sheetnames are present, it creates a directory and
    populates that directory with each merged dataframe. Otherwise, it just writes to one file.
    :param file_df: File dataframe
    :param outfile: file name to write to
    :param delimiter: delimiter
    :return: Nothing
    """
    if len(metadatalist) == 1:
        writer = TextWriter(outfile, delimiter=delimiter)
        writer.write(metadatalist[0].dataframe)
    else:
        folder = os.path.splitext(outfile)[0]
        try:
            create_directory(folder)
            for metadata in metadatalist:
                modifiedOutfile = folder + '/' + metadata.sheetname + '_' + outfile
                writer = TextWriter(modifiedOutfile)
                writer.write(metadata.dataframe)
        except FileExistsError:
            raise FileExistsError(f"Directory '{folder}' already exists")



def write_json(metadatalist, outfile):
    """
        Function: Writes the dataframe to a JSON file. If multiple sheetnames are present, it creates a directory and
        populates that directory with each merged dataframe. Otherwise, it just writes to one file.
        :param file_df: File dataframe
        :param outfile: file name to write to
        :param delimiter: delimiter
        :return: Nothing
        """
    if len(metadatalist) == 1:
        writer = JSONWriter(outfile)
        writer.write(metadatalist[0].dataframe)
    else:
        folder = os.path.splitext(outfile)[0]
        try:
            create_directory(folder)
            for metadata in metadatalist:
                modifiedOutfile = folder + '/' + metadata.sheetname + '_' + outfile
                writer = JSONWriter(modifiedOutfile)
                writer.write(metadata.dataframe)
        except FileExistsError:
            raise FileExistsError(f"Directory '{folder}' already exists")


def write_csv(metadatalist, outfile):
    """
        Function: Writes the dataframe to a CSV file. If multiple sheetnames are present, it creates a directory and
        populates that directory with each merged dataframe. Otherwise, it just writes to one file.
        :param file_df: File dataframe
        :param outfile: file name to write to
        :param delimiter: delimiter
        :return: Nothing
        """
    if len(metadatalist) == 1:
        writer = CSVWriter(outfile)
        writer.write(metadatalist[0].dataframe)
    else:
        folder = os.path.splitext(outfile)[0]
        try:
            create_directory(folder)
            for metadata in metadatalist:
                modifiedOutfile = folder + '/' + metadata.sheetname + '_' + outfile
                writer = CSVWriter(modifiedOutfile)
                writer.write(metadata.dataframe)
        except FileExistsError:
            raise FileExistsError(f"Directory '{folder}' already exists")


def write_pif(metadatalist, outfile):
    """
        Function: Writes the dataframe to a CSV file. If multiple sheetnames are present, it creates a directory and
        populates that directory with each merged dataframe. Otherwise, it just writes to one file.
        :param file_df: File dataframe
        :param outfile: file name to write to
        :param delimiter: delimiter
        :return: Nothing
        """
    if len(metadatalist) == 1:
        writer = PifWriter(outfile)
        writer.write(metadatalist[0].dataframe)
    else:
        folder = os.path.splitext(outfile)[0]
        try:
            create_directory(folder)
            for metadata in metadatalist:
                modifiedOutfile = folder + '/' + metadata.sheetname + '_' + outfile
                writer = PifWriter(modifiedOutfile)
                writer.write(metadata.dataframe)
        except FileExistsError:
            raise FileExistsError(f"Directory '{folder}' already exists")
