import os


def get_folder_size(path_dir):
    total_size = 0
    for path, dirs, files in os.walk(path_dir):
        for f in files:
            path_full = os.path.join(path, f)
            total_size += os.path.getsize(path_full)
    return total_size  # bytes
