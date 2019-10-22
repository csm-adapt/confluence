import sys
import argparse
from .merge import run
from .list_items import list_items


# def parse_args(args):
#     parser = argparse.ArgumentParser(description='parse arguments')
#     parser.add_argument('action', nargs=1, help='sepcifies action of cli')
#
#     args = parser.parse_args(sys)
#



def merge_cli(args):
    parser = argparse.ArgumentParser(description='parse arguments')
    parser.add_argument('infiles', nargs='*', help='input file name with no file type')
    parser.add_argument('-o', '--output', help='output file name')
    parser.add_argument('-i', '--input', nargs=2, help='input file name with accompanying file type', action='append')
    parser.add_argument('-m', '--mergedefault', help='default solution to merge conflicts')
    parser.add_argument('--interactive', action='store_true', help='make the program prompt user for input in case of conflict')
    parser.add_argument('-s', '--sheetname', help='Specify a default sheetname in case writing to an xlsx file')
    parser.add_argument('--outputformat', help='specify output file type')
    parser.add_argument('-q', '--quiet', action='store_true', help='Should a merge conflict happen, default to abort')
<<<<<<< HEAD
    parser.add_argument('k', '--key', help='Specify the name of the smaple name column', default='Sample Name')
    run(parser.parse_args(args))


def list_cli(args):
    parser = argparse.ArgumentParser(description='parse arguments')
    parser.add_argument('list', help='Specifies what to list')
    list_items(args)

=======
    parser.add_argument('-k', '--key', help='Specify the name of the sample name column', default='Sample Name')
    return parser.parse_args(args)
>>>>>>> f4a74cb0eef868b488d8c548af6ef35317be65a6


def cli():
    action = sys.argv[1:2]
    if action[0] == "merge":
         merge_cli(sys.argv[2:])
    elif action[0] == "list":
        list_cli(sys.argv[2:])
    elif action[0] == "info":
        print("Welcome to the confluence interface: PLACE INFO HERE")



# def cli():
#     sys_args = sys.argv[1:2]
    # parser = argparse.ArgumentParser(description='parse arguments')
    # parser.add_argument('action', nargs=1, help='sepcifies action of cli')
    # args = parser.parse_args(sys)
    # if args.action[0] == "merge":
    #     merge_cli(sys.argv[2:1])
    # elif args.action[0] == "list":
    #     list_cli(sys.argv[2:1])
    # elif args.action[0] == "info":
    #     print("Welcome to the confluence interface: PLACE INFO HERE")









# def parse_args(args):
#     parser = argparse.ArgumentParser(description='parse arguments')
#
#     parser.add_argument('action', nargs=1, help='sepcifies action of cli')
#     if args[0] == 'list':
#         parser.add_argument('list', help='Specifies what to list')
#     parser.add_argument('infiles', nargs='*', help='input file name with no file type')
#     parser.add_argument('-o', '--output', help='output file name')
#     parser.add_argument('-i', '--input', nargs=2, help='input file name with accompanying file type', action='append')
#     parser.add_argument('-m', '--mergedefault', help='default solution to merge conflicts')
#     parser.add_argument('--interactive', action='store_true', help='make the program prompt user for input in case of conflict')
#     parser.add_argument('-s', '--sheetname', help='Specify a default sheetname in case writing to an xlsx file')
#     parser.add_argument('--outputformat', help='specify output file type')
#     parser.add_argument('-q', '--quiet', action='store_true', help='Should a merge conflict happen, default to abort')
#     return parser.parse_args(args)
#
# def cli():
#     sys_args = sys.argv[1:]
#     args = parse_args(sys_args)
#     if args.action[0] == 'merge':
#         #print(args.action[0])
#         run(args)
#     elif args.action[0] == 'list':
#         #print(args.action[0])
#         list_items(args)
#     elif args.action[0] == 'info':
#         print("Welcome to the confluence interface: PLACE INFO HERE")


if __name__ == "__main__":
    cli()
