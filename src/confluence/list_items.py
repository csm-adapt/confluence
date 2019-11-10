from .merge import *


def list_items(args):
    print('hello')
    print('action', args.list)
    return{
        'duplicates': list_duplicates
    }[args.list](args)


def list_duplicates(args):
    duplicateList = []
    for file in create_list(args.infiles) + create_list(args.input):
        if guess_file_type(file) == 'xlsx':
            duplicateList = list_duplicates_for_excel(file, duplicateList)
        else:
            duplicateList = list_duplicates_for_other_file_types(file, duplicateList)
    if len(duplicateList) == 0:
        print('No Duplicates')
        return True
    else:
        for i in duplicateList:
            print(i.values, '\n')


def create_list(iterable):
    if iterable is None:
        return []
    else:
        return list(iterable)


def list_duplicates_for_excel(filename, duplicateList):
    sheets = get_sheetnames(filename)
    for sheet in sheets:
        df = read(filename, 'xlsx', sheet).as_dataframe()
        if not df.empty():
            print('\n\n\n\n\n', df.columns,'\n\n\n\n\n')
            duplicates = find_duplicate_sample_names(df)
            if len(duplicates) != 0:
                dictToAdd = {'Filename': filename,
                             'Sheet': sheet,
                             'df': df}
                duplicateList = duplicateList + dictToAdd
    return duplicateList


def list_duplicates_for_other_file_types(filename, duplicateList):
    df = read(filename, guess_file_type(filename), 'Sheet 1').as_dataframe()
    duplicates = find_duplicate_sample_names(df)
    if len(duplicates) != 0:
        dictToAdd = {'Filename': filename,
                     'df': df}
        duplicateList = duplicateList + dictToAdd
    return duplicateList

#todo: pass key name into merge.py
#todo: make it so you can pass empty dataframes to list duplicates