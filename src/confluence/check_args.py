import os


def check(args):
    args = check_for_input_files(args)
    args = check_input(args)
    args = check_output(args)
    return args


def check_input(args):
    if args.input is not None:
        for input in args.input:
            if os.path.exists(input[0]):
                raise IOError('When using -i/--input, specify the file type first, '
                              'then the file name.')
    return args


def check_for_input_files(args):
    if not args.input and not args.infiles:
        raise IOError('Input file(s) not specified')
    return args


def check_output(args):
    #try:
    if args.output is None:
        raise ValueError('Output file not specified')
    return args
    # except ValueError:
    #     ValueError('Output file not specified')


#TODO: check_for_input_files
