"""
Handles merge actions for confluence-merge.
"""

import sys
import argparse


class MergeActions(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs is not None:
            raise ValueError("nargs not allowed")
        super(MergeActions, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, {
            'abort': MergeActions.abort,
            'first': MergeActions.accept_first,
            'second': MergeActions.accept_second,
            'join': MergeActions.return_list,
            'mean': MergeActions.return_mean
        }.get(values, MergeActions.abort))
        # If you want this to throw an error if an invalid action is passed.
        # try:
        #     setattr(namespace, self.dest, {
        #         'abort': MergeActions.abort,
        #         'first': MergeActions.accept_first,
        #         'second': MergeActions.accept_second
        #     }[values])
        # except KeyError:
        #     raise ValueError("Merge action must be one of 'abort', 'first', or 'second'.")

    @staticmethod
    def abort(*args, **kwds):
        sys.exit(1)

    @staticmethod
    def accept_first(*args, **kwds):
        """
        Accepts the first value from a list of arguments.

        :param args: One (or more) list of values
        :param kwds: None. (Used to maintain a constant call signature.)
        :return: The first element in the list of parameters.
        """
        assert len(args) > 0, f"{__name__} requires at least one positional argument."
        return args[0]

    @staticmethod
    def accept_second(*args, **kwds):
        """
        Accepts the second value from a list of arguments.

        :param args: Two (or more) list of values.
        :param kwds: None. (Used to maintain a flexible call signature.)
        :return: The second element in a list of parameters.
        """
        assert len(args) > 1, f"{__name__} requires at least two positional arguments."
        return args[1]

    @staticmethod
    def return_list(*args):
        return str(list(args))

    @staticmethod
    def return_mean(*args):
        try:
            return (float(args[0]) + float(args[1])) / 2
        except:
            raise ValueError('Arguments must be integers or floats to get average.')

    @staticmethod
    def take_keyword(args):
        """
        Function: This takes a number between 1 and 5 and outputs the corresponding value of the array, or aborts the
        merge if that is what the user chooses.
        :param argument: keyboard entry from the user
        :param values: list of the possible valuse for the user to chose
        :return: value chosen by the user
        """
        try:
            key = int(input('Enter the number\n'))
            return{
                1: MergeActions.accept_first,
                # value from file 1
                2: MergeActions.accept_second,
                # value from file 2
                3: MergeActions.return_list,
                # list of both of them
                4: MergeActions.return_mean,
                # take average of values
                5: MergeActions.abort,
                # abort merge
            }[key](args)
        except:
            raise KeyError('Invalid selection.')


class InfilesActions(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        valuelist = []
        for value in values:
            Values = self.Values()
            Values.filename = value
            valuelist.append(Values)
        setattr(namespace, self.dest, valuelist)

    @staticmethod
    class Values:
        filename = None
        ftype = None


class InteractiveActions:
    def __call__(self, file1, file2, sheetname, sample, column, value1, value2):
        return InteractiveActions.interactive(file1, file2, sheetname, sample, column, value1, value2)

    @staticmethod
    def interactive(file1, file2, sheetname, sample, column, value1, value2):
        print(InteractiveActions.message(file1, file2, sheetname, sample, column, value1, value2))
        return MergeActions.take_keyword([value1, value2])

    @staticmethod
    def message(file1, file2, sheetname, sample, column, value1, value2):
        return (f"Merge conflict between '{file1}' and '{file2}' in sheet'{sheetname}"
                f"'for sample '{sample}' under column '{column}"
                f"\n1: Accept value '{value1}' from file {file1}"
                f"\n2: Accept value '{value2}' from file {file2}"
                f"\n3: Join values into a list"
                f"\n4: Take average (mean)"
                f"\n5: Abort the merge\n")