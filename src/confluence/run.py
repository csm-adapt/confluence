from .merge import *
from .Write import write
import sys


def run(args):
    """
    Function: This is the function called when the merge.py is used in the terminal.
    :param args: An array of files to be merged
    :return: None
    """
    args = check(args)
    # This checks the parse_args function
    set_global_variables(args)
    # This sets all the default variables. A user might enter a default action for the program to do in case of a
    # merge conflict (e.g. abort the merge, chose the value from the first file, let the user decide). These variables
    # initialize to 'None' if no default action is specified.
    file_df = create_df_of_all_infiles(args)
    # This creates a large dataframe containing the file name, the corresponding dataframe, the file type, and the
    # sheetname. This is the object that will be passed to the write function.
    write(file_df, get_file(args.output, args.outputformat), args.outputformat)
    # This function will write the dataframes to the output file.


if __name__ == "__main__":
    run(sys.argv[1:])