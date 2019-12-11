import sys
import argparse
from .list_items import list_items
from .pif_maker import convert
from .merge import run as merge_main
from .merge import generate_merge_args
from .list_items import list_items as list_main
from .list_items import generate_list_args

# class CLIparser():
#     def __init__(self):
#         self.parser = None
#         self.set_arguments()
#
#     def set_arguments(self):
#         self.parser = argparse.ArgumentParser(description='parse arguments')
#         subparsers = self.parser.add_subparsers(help='subparser help')
#
#         merge_parser = subparsers.add_parser('merge', help='merge help')
#         merge_parser.add_argument('infiles', nargs='*', help='input file name with no file type')
#         merge_parser.add_argument('-o', '--output', help='output file name')
#         merge_parser.add_argument('-i', '--input', nargs=2, help='input file name with accompanying file type', action='append')
#         merge_parser.add_argument('-m', '--mergedefault', help='default solution to merge conflicts')
#         merge_parser.add_argument('--interactive', action='store_true', help='make the program prompt user for input in case of conflict')
#         merge_parser.add_argument('-s', '--sheetname', help='Specify a default sheetname in case writing to an xlsx file')
#         merge_parser.add_argument('--outputformat', help='specify output file type')
#         merge_parser.add_argument('-q', '--quiet', action='store_true', help='Should a merge conflict happen, default to abort')
#         merge_parser.add_argument('-k', '--key', help='Specify the name of the smaple name column', default='Sample Name')
# s
#         list_parser = subparsers.add_parser('list', help='list help')
#         list_parser.add_argument('action', help ='specifies action')
#         list_parser.add_argument('-i', '--input', nargs=2, help='input file name with accompanying file type', action='append')
#         list_parser.add_argument('infiles', nargs='*', help='input file name with no file type')
#         list_parser.add_argument('-k', '--key', help='Specify the name of the smaple name column', default='Sample Name')
#         list_parser.set_defaults(func=list_items)
#
#         pif_parser = subparsers.add_parser('makePIF', help='PIF help')
#         pif_parser.add_argument('input_file', help='specifies file to convert to PIF')
#         pif_parser.set_defaults(func=convert)
#
#
#     def parse_args(self):
#             args = self.parser.parse_args(sys.argv[1:])
#             return args
#
#
# def main():
#     args = CLIparser().parse_args()
#
#
# if __name__ == '__main__':
#     main()
#

################################################################################################
################################################################################################

def parse_args(args):

    if isinstance(args, list):
        parser = argparse.ArgumentParser(
        description="Comand Line Tool for Confluence",
        help = "Comand Line Tool for Confluence")
    else:
        parser = args

    subparsers = parser.add_subparsers(
        title = "Commands",
        required = True,
        help = "Operations availible from confluence CLI")

    #Merge Parser
    merge_parser = subparsers.add_parser('merge', help='merge help')
    merge_parser.set_defaults(func = merge_main)
    generate_merge_args(merge_parser)

    #List Parser
    list_parser = subparsers.add_parser('list', help='list help')
    list_parser.set_defaults(func = list_main)
    generate_list_args(list_parser)



def main():
    args = sys.argv[1:]
    if isinstance(args,list):
        args = parse_args(args)


if __name__ == '__main__':
    main()


%return parser

##main calls logging,

################################################################################################
################################################################################################
