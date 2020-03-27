from confluence.subcommands.duplicates import main as duplicates_main
from testfixtures import LogCapture

def test_duplicated():
    cli = ['test_files/121-ABC.xlsx',
           'test_files/123-DEF.xlsx',
           '--index-column', 0]
    with LogCapture() as l:
        duplicates_main(cli)
        assert ('confluence.subcommands.duplicates',
                'WARNING',
                " Duplicated row(s) '[1]' found in file 'test_files/121-ABC.xlsx' in sheet "
                 "'Sheet1'.") in l.actual()
