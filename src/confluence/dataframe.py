from .global_variables import *
import pandas as pd
import numpy as np


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
    if df.empty:
        return df
    combined = create_empty_df()
    duplicates = find_duplicate_sample_names(df)
    # creates an array of all the repeated sample names
    for repeatedName in duplicates:
        temp = df[df[get_sample_name_column()] == repeatedName]
        # creates a temporary dataframe with only the rows with the repeated name
        combined = join_two_dataframes(combined, combiner(temp))
        # There might be several different repeated names. There will be one row for each fixed name, so 'combined'
        # will contain each of these rows. 'Combiner' will be the function that merges the rows.
    dfWithoutDuplicates = df.drop_duplicates(subset=[get_sample_name_column()], keep=False)
    # Deletes all repeated rows from the original dataframe
    return join_two_dataframes(dfWithoutDuplicates, combined)


def join_many_dataframes(dataframes):
    """
    :param dfs: list of the dataframes
    :return: concatenated dataframe
    """
    combined = create_empty_df()
    for df in dataframes:
        combined = pd.concat([combined, df], sort=False, ignore_index=True)
    return combined


def check_two_dfs_for_merge_conflict(leftDataframe, rightDataframe, sheetname):
    df = join_two_dataframes(leftDataframe, rightDataframe)
    duplicates = find_duplicate_sample_names(df)
    for name in duplicates:
        temp = df[df[get_sample_name_column()] == name]
        for column in temp.loc[:, temp.columns != 'Filename']:
            # This for loop iterates through each of the columns in the temporary dataframe to check how many
            # unique entries are in each. If the answer is more than one, it calls the 'make_user_choose_two_files'
            # function.
            instances = temp[column].nunique()
            if instances > 1:
                # The above if statement checks if there is more than one unique value per column. If the global default
                # variable is (None), then it prompts the user to choose which value to accept. Then, it changes the
                # values in each dataframe to match this.
                choice = make_user_choose_between_two_files(temp[column].values,
                                                            temp['Filename'].values[0],
                                                            temp['Filename'].values[1],
                                                            column,
                                                            temp[get_sample_name_column()].values[0],
                                                            sheetname)
                df.at[df[get_sample_name_column()] == name, column] = choice
                # Fix this later
    return df


def find_duplicate_sample_names(df):
    if df.empty:
        return []
    else:
        column = get_sample_name_column()
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


def check_for_sample_name_completeness(df, filename, sheetname, ftype):
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
        if pd.isna(list(df[get_sample_name_column()])[i]) is True:
            raise IOError(f"Empty cell in sample name in row {i + 1} in file {filename} in sheet {sheetname}")
    return df
    #except IOError:
    #    IOError(f"Empty cell in sample name in row {i + 1} in file {filename} in sheet {sheetname}")


def check_for_sample_name_uniqueness(df, filename, sheetname, ftype):
    """
    Functionality: Makes sure there are no repeated sample names, similar to the 'check_for_merge_conflict' function
    :param df: dataframe to check
    :param filename: name of the file
    :param sheetname: name of the sheet
    :param column: column that is being checked
    :return: fixed dataframe
    """
    duplicates = find_duplicate_sample_names(df)
    for name in duplicates:
        temp = df[df[get_sample_name_column()] == name]
        for column in temp:
            instances = temp[column].nunique()
            if instances > 1:
                # choice = make_user_choose_within_one_file(temp[column].values,
                #                                           list(temp.index.values),
                #                                           column,
                #                                           filename,
                #                                           sheetname,
                #                                           temp[get_sample_name_column()].values[0])
                # df.loc[df[get_sample_name_column()] == name, column] = choice
                # raise ValueError(f'Conflicting values found within file {filename} ' +
                #                  (f'in sheet {sheetname}' if ftype == 'xlsx' else '') +
                #                  (f'under column {column}' )+
                #                  (f'for the sample {name}'))
                display_conflicting_values_error(temp[column].values,
                                                 list(temp.index.values),
                                                 column,
                                                 filename,
                                                 sheetname,
                                                 temp[get_sample_name_column()].values[0],
                                                 ftype)
    return fix_dataframe(df)


def check_sample_name_is_represented_in_dataframe(df, filename, sheetname, ftype):
    sampleName = get_sample_name_column()
    if sampleName not in df.columns:
        errorMessage = ((f"The sample name '{sampleName}' is not a column name in file '{filename}' ") +
                        (f"within sheet '{sheetname}'." if ftype == 'xlsx' else '.'))
        raise KeyError(errorMessage)
    return df


def create_empty_df(header=None):
    """
    Function: Pretty self explanitory. Just creates an empty dataframe with no rows or columns. We can specify
    header values by giving it an array, such as create_empty_df(['header1', 'header2', 'header3'])
    :param header: an array of all the column names we want
    :return: an empty dataframe
    """
    return pd.DataFrame(columns=header)


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
    if df.empty:
        return df
    combined = create_empty_df()
    duplicates = find_duplicate_sample_names(df)
    # creates an array of all the repeated sample names
    for repeatedName in duplicates:
        temp = df[df[get_sample_name_column()] == repeatedName]
        # creates a temporary dataframe with only the rows with the repeated name
        combined = join_two_dataframes(combined, combiner(temp))
        # There might be several different repeated names. There will be one row for each fixed name, so 'combined'
        # will contain each of these rows. 'Combiner' will be the function that merges the rows.
    dfWithoutDuplicates = df.drop_duplicates(subset=[get_sample_name_column()], keep=False)
    # Deletes all repeated rows from the original dataframe
    return join_two_dataframes(dfWithoutDuplicates, combined)


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
    df_valid = df.groupby(by=get_sample_name_column()).agg(dict.fromkeys(df.columns[0:], check_if_nan))
    return df_valid


def join_two_dataframes(lhs, rhs):
    """
    :param lhs: dataframe one
    :param rhs: second dataframe
    :return: concatenated dataframe
    """
    return pd.concat([lhs, rhs], sort=False, ignore_index=True)


def display_conflicting_values_error(values, rows, column, filename='None', sheetname='Sheet1', sample='None', ftype = None):
    # rowList = ['\nRow ' + str(rows[i]) + ': ' + str(values[i]) for i in range(len(values))]
    # displayRows = ''
    # for row in rowList:
    #     displayRows = displayRows + row
    errorMessage = ((f'Conflicting values found within file {filename} ') +
                    (f'in sheet {sheetname} ' if ftype == 'xlsx' else '') +
                    (f'under column {column} ') +
                    (f'for sample {sample}. Aborting merge.')
                    )
    raise ValueError(errorMessage)


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
    if get_default_action() is not None:
        return take_keyword(convert_merge_default_into_number(get_default_action()), arr)
    else:
        print('Merge conflict between', file1, 'and', file2, 'in sheet',
              sheetname, 'for sample', sample, 'under column', column, '\n',
              '\n1: Accept value', arr[0], 'from file', file1,
              '\n2: Accept value', arr[1], 'from file', file2,
              '\n3: Join values into a list',
              '\n4: Take average (mean)',
              '\n5: Abort the merge\n')
        return take_keyword(int(input('Enter the number\n')), arr)


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
            'mean': 4,
            'abort': 5
        }[input]
    except KeyError:
        raise KeyError(f"{input} is not a recognized default action")


def make_user_choose_within_one_file(values, rows, column, filename='None', sheetname='Sheet1', sample='None'):
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
    if get_default_action() is not None:
        return take_keyword(convert_merge_default_into_number(get_default_action()), [values[0], values[-1]])
    print("Multiple values found in '", filename, "' in sheet '",
          sheetname, "' for sample '", sample, "' under column '", column, "'")
    for i in range(len(values)):
        print('', i+1, ':', 'Take value', values[i], 'from row', rows[i]+1)
    print('', len(values)+1, ': Join values into a list\n',
          len(values)+2, ': Take average (mean)\n',
          len(values)+3, ': Abort merge\n')
    return take_keyword_one_file(int(input('Enter the number of the value\n')), values)


def take_keyword_one_file(input, values):
    """
    Function: This takes a number between 1 and 5 and outputs the corresponding value of the array, or aborts the
    merge if that is what the user chooses.
    :param argument: keyboard entry from the user
    :param values: list of the possible valuse for the user to chose
    :return: value chosen by the user
    """
    if input <= len(values):
        return values[input-1]
    else:
        input = input - len(values)
        action = {
            1: str(list(values)),
            # list of both of them
            2: (values[0]+values[1])/2,
            # take average of values
            3: 'exit',
            # abort merge
        }
        if action.get(input) is 'exit':
            raise ValueError('Aborting merge due to merge conflict')
        selectedIndex = action.get(input, "Invalid selection. Aborting merge.")
        return selectedIndex