import os


def create_dir_if_not_exists(path: str):
    """
    Creates the directory for the specified path which may be a file path or directory path.
    """
    if not os.path.isdir(path):
        path = os.path.dirname(path)

    if not os.path.exists(path):
        os.makedirs(path)


def create_file_if_not_exists(file_path: str):

    if os.path.exists(file_path):
        return

    create_dir_if_not_exists(file_path)
    with open(file_path, "a"):
        pass
