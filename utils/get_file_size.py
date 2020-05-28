import os


def get_file_size(path_file):
    file_size = os.stat(path_file).st_size
    return file_size  # bytes

