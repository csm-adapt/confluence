def set_key_variable(columnName='Sample Name'):
    global key
    key = columnName


def get_sample_name_column():
    return key


def set_global_variables(args=None, Default='abort', TxtSheetname='Sheet1', Key='Sample Name'):
    """
    Function: initialize the global variables. As of now, there are two, but I might add more later.
    :param args:
    :type argparse object
    :param default:
    :type str
    :param txtSheetname = sheetname for excel files when reading non-excel inputs
    :type str
    :param Key: column name that acts as sample name
    :return: None
    """
    global default
    global txtSheetname
    global key
    if args:
        default = find_default_action(args)
        txtSheetname = args.sheetname if args.sheetname else 'Sheet1'
        key = args.key
        # This gives the user an option to specify a sheetname for non-excel files, otherwise the default name is 'Sheet1'
    else:
        default = Default
        txtSheetname = TxtSheetname
        key = Key


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

def get_default_action():
    return default


def get_txt_sheetname():
    return txtSheetname
