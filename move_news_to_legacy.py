import shutil
import os
from pathlib import Path


def move_news_files(source_dir: str = "news", dest_dir: str = "legacy_news") -> None:
    """
    Moves all .csv and .txt files from the source folder to the destination folder.

    Parameters:
    - source_dir (str): The directory containing the files to move.
    - dest_dir (str): The destination directory where files will be moved.

    If no matching files are found, a message will be displayed.
    """
    # Create destination folder if it doesn't exist
    os.makedirs(dest_dir, exist_ok=True)

    # Track if any files were moved
    files_moved = False

    # Move CSV and TXT files
    for file_extension in ["*.csv", "*.txt"]:
        for file in Path(source_dir).glob(file_extension):
            shutil.move(str(file), dest_dir)
            files_moved = True

    # Display appropriate message
    if files_moved:
        print(f"All matching files have been moved to {dest_dir}.")
    else:
        print(f"No .csv or .txt files found in {source_dir}.")
