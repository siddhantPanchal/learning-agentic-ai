import os
from typing import Literal


def list_directory_tool() -> list[str]:
    """
    Returns a list of files and directories in the current working directory.

    Returns:
        list[str]: The names of files and directories in the current directory.
    """
    try:
        return os.listdir(os.getcwd())
    except Exception as e:
        raise Exception(f"Failed to list directory: {e}")


def read_file_tool(path: str) -> list[str]:
    """
    Reads and returns the contents of a file.

    Args:
        path (str): the path of the file.

    Returns:
        list[str]: the contents of the file.
    """

    if not os.path.exists(path):
        raise Exception(f"File not found: {path}")
    with open(path, 'r') as f:
        return f.readlines()


def write_file_tool(path: str, content: str, mode: Literal['w', 'a'] = 'w') -> None:
    """
    Writes content to a file. If the file does not exist, it will be created.

    Args:
        path (str): the path of the file.
        content (str): the text to write into the file.
        mode (Literal['w', 'a']): 'w' to overwrite existing content, 'a' to append. Defaults to 'w'.
    """
    # Removed the os.path.exists check so 'w' and 'a' modes can create new files natively.
    with open(path, mode) as f:
        f.write(content)


def delete_file_tool(path: str) -> None:
    """
    Deletes the specified file from the filesystem.

    Args:
        path (str): the path of the file to delete.
    """
    if not os.path.exists(path):
        raise Exception(f"File not found: {path}")
    os.remove(path)
