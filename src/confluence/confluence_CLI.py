import sys
import argparse
from .merge import run
from .list_items import list_items
from .pif_maker import convert




#
# def merge_cli(args):
#     parser = argparse.ArgumentParser(description='parse arguments')
#     parser.add_argument('infiles', nargs='*', help='input file name with no file type')
#     parser.add_argument('-o', '--output', help='output file name')
#     parser.add_argument('-i', '--input', nargs=2, help='input file name with accompanying file type', action='append')
#     parser.add_argument('-m', '--mergedefault', help='default solution to merge conflicts')
#     parser.add_argument('--interactive', action='store_true', help='make the program prompt user for input in case of conflict')
#     parser.add_argument('-s', '--sheetname', help='Specify a default sheetname in case writing to an xlsx file')
#     parser.add_argument('--outputformat', help='specify output file type')
#     parser.add_argument('-q', '--quiet', action='store_true', help='Should a merge conflict happen, default to abort')
#     parser.add_argument('-k', '--key', help='Specify the name of the smaple name column', default='Sample Name')
#     run(parser.parse_args(args))
#
#
# def list_cli(args):
#     parser = argparse.ArgumentParser(description='parse arguments')
#     parser.add_argument('list', help='Specifies what to list')
#     list_items(args)
#
#
#
# def cli():
#     action = sys.argv[1:2]
#     if action[0] == "merge":
#          merge_cli(sys.argv[2:])
#     elif action[0] == "list":
#         list_cli(sys.argv[2:])
#     elif action[0] == "info":
#         print("Welcome to the confluence interface: PLACE INFO HERE")
#
#



def cli():
    action = sys.argv[1:]

    parser = argparse.ArgumentParser(description='parse arguments')
    parser.add_argument('--action')
    subparsers = parser.add_subparsers(help ='subparser help')

    #merge CLI
    merge_parser = subparsers.add_parser('merge', help='merge help')
    merge_parser.add_argument('infiles', nargs='*', help='input file name with no file type')
    merge_parser.add_argument('-o', '--output', help='output file name')
    merge_parser.add_argument('-i', '--input', nargs=2, help='input file name with accompanying file type', action='append')
    merge_parser.add_argument('-m', '--mergedefault', help='default solution to merge conflicts')
    merge_parser.add_argument('--interactive', action='store_true', help='make the program prompt user for input in case of conflict')
    merge_parser.add_argument('-s', '--sheetname', help='Specify a default sheetname in case writing to an xlsx file')
    merge_parser.add_argument('--outputformat', help='specify output file type')
    merge_parser.add_argument('-q', '--quiet', action='store_true', help='Should a merge conflict happen, default to abort')
    merge_parser.add_argument('-k', '--key', help='Specify the name of the smaple name column', default='Sample Name')
    merge_parser.set_defaults(func=run)

    #list CLI
    list_parser = subparsers.add_parser('list', help='list help')
    list_parser.add_argument('action', help ='specifies action')
    list_parser.add_argument('-i', '--input', nargs=2, help='input file name with accompanying file type', action='append')
    list_parser.add_argument('infiles', nargs='*', help='input file name with no file type')
    list_parser.set_defaults(func=list_items)
    list_parser.add_argument('-k', '--key', help='Specify the name of the smaple name column', default='Sample Name')
    print(parser.action)

    #PIF maker CLI
    pif_parser = subparsers.add_parser('makePIF', help='PIF help')
    pif_parser.add_argument('input_file', help='specifies file to convert to PIF')
    pif_parser.set_defaults(func=convert)




if __name__ == "__main__":
    cli()
