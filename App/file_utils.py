import os


def ensure_folder_exists(folder):
    """
    Ensures the specified folder exists. Creates it if it doesn't exist.
    """
    os.makedirs(folder, exist_ok=True)
