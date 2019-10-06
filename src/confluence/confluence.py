import sys
import argparse
from merge import run


def parse_args(args):
    parser = argparse.ArgumentParser(description='parse arguments')
    parser.add_argument('action', nargs=1, help='sepcifies action of cli')
    parser.add_argument('infiles', nargs='*', help='input file name with no file type')
    parser.add_argument('-o', '--output', help='output file name')
    parser.add_argument('-i', '--input', nargs=2, help='input file name with accompanying file type', action='append')
    parser.add_argument('-m', '--mergedefault', help='default solution to merge conflicts')
    parser.add_argument('--interactive', action='store_true', help='make the program prompt user for input in case of conflict')
    parser.add_argument('-s', '--sheetname', help='Specify a default sheetname in case writing to an xlsx file')
    parser.add_argument('--outputformat', help='specify output file type')
    parser.add_argument('-q', '--quiet', action='store_true', help='Should a merge conflict happen, default to abort')
    return parser.parse_args(args)

def cli(sys_args):

    args = parse_args(sys_args)
    if args.action[0] == 'merge':
        print(args.action[0])
        run(args)
    elif args.action[0] == 'info':
        print("Welcome to the confluence interface: PLACE INFO HERE")


if __name__ == "__main__":
    cli(sys.argv[1:])
