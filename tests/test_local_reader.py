"""
Questions:

Why use the zip function rather than comparing the files separately?

Why compare by pointer?

What is the function of the basereader class and how does it interact with other readers?
"""

import pytest
from confluence.read import LocalReader


#@pytest.fixture
def foo_contents():
    return [
        "Hello\n",
        "World.\n"
    ]

@pytest.fixture
def test_filename():
    return "foo.txt"

@pytest.fixture
def expected_file_contents():
    return ["Hello","World."]

def test_LocalReader(expected_file_contents, test_filename):
    pass


def test_LocalReader(foo_contents):
    # test empty constructor
    reader = LocalReader('foo.txt')
    for actual, expected in zip(reader, foo_contents):
        assert actual == expected
    actual = reader.read()
    expected = foo_contents()
    assert actual == expected
    print(actual)
    print(expected)
    reader.close()
    # test filename as part of constructor
    #for actual, expected in zip(reader, foo_contents):
    #    assert actual == expected

test_LocalReader(foo_contents)


#test_LocalReader(foo_contents)
# def test_LocalReader_context(foo_contents):
#     with LocalReader('foo.txt') as ifs:
#         for actual, expected in zip(ifs, foo_contents):
#             assert actual == expected
