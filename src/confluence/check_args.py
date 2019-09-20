import os

def check(args):
    args = check_output(args)
    args = check_input(args)
    return args

def check_output(args):
    #try:
    if args.output is None:
        raise ValueError('Output file not specified')
    return args
    # except ValueError:
    #     ValueError('Output file not specified')


def check_input(args):
    if args.input is not None:
        if os.path.exists(args.input[0]):
            raise IOError('When using -i/--input, specify the file type first, '
                          'then the file name.')
    return args
