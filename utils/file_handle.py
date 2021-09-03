import os


def save_file(data: str, filepath: str):
    with open(filepath, "wb") as file:
        file.write(data)


def delete_file(file_path: str):
    os.remove(file_path)
