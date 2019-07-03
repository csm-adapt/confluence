import os


def read_file(fileName):
    """
    Function: read_file
    -------------------
    Opens a file, creates an array, and puts each line from the file into the array

    fileName: the name of the file in string format, with ".txt" or ".json"
    folderPath: the current working directory of the desired file

    returns: array that contains each line of the file.

    :Example:
    :code: `python`
        with open(fileName, 'rb') as ifs:
            lines = ifs.readlines()
    """
    pass


folderPath = os.getcwd()
fileName = "example1.txt"
exampleArray = read_file(fileName, folderPath)

for i in range (len(exampleArray)):
    print(exampleArray[i],"\n")


#def write_file(fileName, folderPath, data):
def write_file(fileobj, overwrite=False)
    """
    Function: write_file
    --------------------------------------
    Opens a file (if no file by that name exists, creates a new file), creates an array, and puts each line from the file into the array

    fileName: the name of the file in string format, with ".txt" or ".json"
    folderPath: the current working directory of the created file
    data: the line of data (string format) that goes into the 
    
    Parameters
    ==========
    :param fileobj: File object to which to write.
    :type fileobj: str or any object that exposes a write method.
    :param overwrite: Whether to overwrite the file if it already exists.
        This is only valid if fileobj is a string.
    :type overwrite: bool

    :return: None
    
    :Example:
    :code: `python`
        # library for operating system (OS) functions
        import os
        # does the file exist, and do we want to overwrite if so.
        if os.path.isfile(fileName) and not overwrite:
            raise IOError(f"{ofile} exists. Set overwrite=True to overwrite.")
        # if the file object is a string, then open the corresponding filename
        if isinstance(fileobj, str):
            ofs = open(fileobj, "wb")
        else:
            # otherwise, assume the file object is a file, StringIO, etc. that exposes a write method.
            ofs = fileobj
        # write the data
        ofs.write(data)
        # if the file object was a string, then we opened it and should close it.
        if fileobj is not ofs:
            ofs.close()
        return
    """
    pass


folderPath = os.getcwd()
fileName = "example1.txt"
exampleArray = [0,1,2,3,4]
array = exampleArray

for i in range(len(exampleArray)):
    data = array[i]
    write_file(fileName, folderPath, data)