from .merge import *


# def generate_list_args(description):
#     def parse_args(args):
#
#         if isinstance(args,list):
#             parser = argparse.ArgumentParser(description = description)
#         else:
#             parser = args
#
#         parser.add_argument('infiles', nargs='*', help='input file name with no file type')
#         parser.add_argument('-o', '--output', help='output file name')
#         parser.add_argument('-i', '--input', nargs=2, help='input file name with accompanying file type', action='append')
#         parser.add_argument('-m', '--mergedefault', help='default solution to merge conflicts')                merge_parser.add_argument('--interactive', action='store_true', help='make the program prompt user for input in case of conflict')
#         parser.add_argument('-s', '--sheetname', help='Specify a default sheetname in case writing to an xlsx file')
#         parser.add_argument('--outputformat', help='specify output file type')
#         parser.add_argument('-q', '--quiet', action='store_true', help='Should a merge conflict happen, default to abort')
#         parser.add_argument('-k', '--key', help='Specify the name of the smaple name column', default='Sample Name')
#
#         if isinstance(args, list):
#             return parser.parse_args(args)
#     return parse_args
#

def generate_list_args(description):
    def parse_args(args):

        if isinstance(args,list):
            parser = argparse.ArgumentParser(description = description)
        else:
            parser = args

        list_parser.add_argument('action', help ='specifies action')
        list_parser.add_argument('-i', '--input', nargs=2, help='input file name with accompanying file type', action='append')
        list_parser.add_argument('infiles', nargs='*', help='input file name with no file type')
        list_parser.add_argument('-k', '--key', help='Specify the name of the smaple name column', default='Sample Name')

        if isinstance(args, list):
            return parser.parse_args(args)
    return parse_args



def list_items(args):
    set_key_variable(args.key)
    return{
        'duplicates': list_duplicates
    }[args.action](args)


def list_duplicates(args):
    duplicateList = []
    for file in create_list(args.infiles) + create_list(args.input):
        if guess_file_type(file) == 'xlsx':
            duplicateList = list_duplicates_for_excel(file, duplicateList, args.key)
        else:
            duplicateList = list_duplicates_for_other_file_types(file, duplicateList)
    if len(duplicateList) == 0:
        print('No Duplicates')
        return True
    else:
        for i in duplicateList:
            for key in i:
                print(key, ': ', i[key])


def create_list(iterable):
    if iterable is None:
        return []
    else:
        return list(iterable)


def list_duplicates_for_excel(filename, duplicateList, key):
    sheets = get_sheetnames(filename)
    for sheet in sheets:
        df = read(filename, 'xlsx', sheet).as_dataframe()
        if not df.empty:
            df = df.drop_duplicates(subset=key)
            duplicates = find_duplicate_sample_names(df)
            if len(duplicates) != 0:
                dictToAdd = {'Filename': filename,
                             'Sheet': sheet,
                             'Duplicates': duplicates}
                duplicateList = duplicateList + [dictToAdd]
    return duplicateList


def list_duplicates_for_other_file_types(filename, duplicateList):
    df = read(filename, guess_file_type(filename), 'Sheet 1').as_dataframe()
    duplicates = find_duplicate_sample_names(df)
    if len(duplicates) != 0:
        dictToAdd = {'Filename': filename,
                     'Duplicates': duplicates}
        duplicateList = duplicateList + [dictToAdd]
    return duplicateList


if __name__ == "__main__":
    list_items(sys.argv[1:])

#todo: pass key name into merge.py
#todo: make it so you can pass empty dataframes to list duplicates

#todo: make an error message that tells the user there is no sample name
