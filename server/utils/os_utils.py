import os


def create_dir_if_not_exists(path: str):
    if not os.path.isdir(path):
        path = os.path.dirname(path)

    if not os.path.exists(path):
        os.makedirs(path)


def create_file_if_not_exists(file_path: str):
    if not os.path.exists(file_path):
        create_dir_if_not_exists(file_path)
        with open(file_path, "a"):
            pass
