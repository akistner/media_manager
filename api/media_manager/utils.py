"""Utility module for handling dates and file extensions."""

import hashlib
import logging
import os
import re
from datetime import datetime
from typing import Optional

# Configures the application's logger.
log_config = {
    'level': logging.ERROR,
    'format': '%(asctime)s [%(levelname)s]: %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
    'encoding': 'utf-8'
}
logging.basicConfig(**log_config)
logger = logging.getLogger(__name__)

# Global variable to control checksum records.
checksum_control = {}


def _is_valid_date(date: str) -> bool:
    """
    Check if the given date string is in the 'YYYYMMDD' format.
    """
    try:
        datetime.strptime(date, '%Y%m%d')
        return True
    except ValueError as e:
        message = 'It is not in the "YYYYMMDD" format. %s'
        logger.error(message, e)
        return False


def _calculate_checksum(file_path: str, algorithm: str = 'md5', block_size: int = 65536) -> str:
    """
    Calculates the checksum (hash) of a file using the specified algorithm.

    Parameters:
    - file_path (str): The path to the file for which to calculate the checksum.
    - algorithm (str, optional): The hash algorithm to use. Options: 'md5', 'sha256', 'sha3'.
    - block_size (int, optional): The block size for reading the file in bytes. Default is 65536.

    Returns:
    - str: The hexadecimal representation of the calculated checksum.
    """

    if algorithm == 'md5':
        hash_function = hashlib.md5()
    elif algorithm == 'sha256':
        hash_function = hashlib.sha256()
    elif algorithm == 'sha3':
        hash_function = hashlib.sha3_256()
    else:
        raise ValueError("Invalid algorithm. Options: 'md5', 'sha256', 'sha3'.")

    with open(file_path, 'rb') as file:
        for block in iter(lambda: file.read(block_size), b''):
            hash_function.update(block)

    return hash_function.hexdigest()


def get_media_directories() -> (str, str):
    """
    Configures the directories for the application.

    Returns:
        str: The path to the media directory.
        str: The path to the output directory.
    """

    # Get the current working directory.
    script_dir = os.path.dirname(__file__)

    # Define constants for directories.
    input_dir_name = 'input'
    output_dir_name = 'output'

    # Define the path for the input directory.
    input_dir = os.path.join(script_dir, '..', '..', input_dir_name)
    input_dir = os.path.normpath(input_dir)

    # Check if the input directory exists. If it doesn't, create it.
    os.makedirs(input_dir, exist_ok=True)

    # Define the path for the output directory.
    output_dir = os.path.join(script_dir, '..', '..', output_dir_name)
    output_dir = os.path.normpath(output_dir)

    # Check if the output directory exists. If it doesn't, create it..
    os.makedirs(output_dir, exist_ok=True)

    return input_dir, output_dir


def get_file_extension(file_name: str) -> str:
    """
    Obtains the file extension from a file name.
    """
    file_extension = file_name.split('.')
    file_extension = file_extension[len(file_extension) - 1]
    file_extension = file_extension.lower()
    if file_extension == 'jpeg':
        file_extension = 'jpg'
    return file_extension


def reformat_date(date: str) -> Optional[str]:
    """
    Reformat the given date string to 'YYYYMMDD' format if necessary.
    """
    # Get the digits.
    date = re.sub('[^0-9]', '', date)

    # Check if the original date is already in "YYYYMMDD" format.
    if _is_valid_date(date):
        # Return the original date.
        return date

    # Replace the date in "DDMMYYYY" format with "YYYYMMDD".
    # pattern = r'(\d{2})(\d{2})(\d{4})'
    # new_date = re.sub(pattern, r'\3\2\1', date)

    return None


def remove_time_from_filename(file_name: str) -> str:
    """
    Remove the time '_000000' from the given file name.

    Args:
        file_name (str): The original file name.

    Returns:
        str: The new file name after removing '_000000'.
    """
    # Check if '_000000' is present in the file name.
    if '_000000' in file_name:
        new_file_name = file_name.replace('_000000', '')
        return new_file_name

    # If '_000000' is not present, return the original file name.
    return file_name


def exist_valid_dates(media_metadata: dict) -> bool:

    """
    Check if the provided media metadata dictionary contains valid date fields.

    Args:
        media_metadata (dict): A dictionary containing metadata information for media.

    Returns:
        bool: True if the dictionary contains valid date fields, False otherwise.

    The function checks if 'date_time_modified' and 'earliest_date' are the only datetime fields.
    If the conditions are met, the function returns False, indicating that the dates are not valid.
    Otherwise, it returns True, indicating that the dates are valid.
    """

    # Get all keys of datetime type in the dictionary.
    datetime_keys = [key for key, value in media_metadata.items() if isinstance(value, datetime)]

    # Check if "date_time_modified" and "earliest_date" are the only datetime fields.
    if datetime_keys == ['date_time_modified', 'earliest_date']:
        return False

    return True


def exist_prior_checksum(file_path: str, media_metadata: dict) -> bool:
    """
    Check if a prior checksum for the given file exists in the checksum control.

    Args:
        file_path (str): The path to the file for which to check the checksum.
        media_metadata (dict): Metadata associated with the media file.

    Returns:
        bool: True if a prior checksum for the file exists in the checksum control, False otherwise.
    """

    # Calculate the checksum for the file using the "sha3" algorithm.
    checksum = _calculate_checksum(file_path, 'sha3')

    # Check if the calculated checksum is present in the checksum control.
    if checksum in checksum_control:
        # A prior checksum exists for the file.
        return True

    # If the checksum is not present, add it to the checksum control along with the file path.
    checksum_control[checksum] = media_metadata['path']

    # No prior checksum found for the file.
    return False


def handle_counter(name: str, destination_path: str) -> str:
    """
    Rename the file with a counter if necessary to avoid naming conflicts.

    Parameters:
    - name (str): Name of the file to be saved.
    - destination_path (str): Path to the destination folder.

    Returns:
    - str: Adjusted name of the file, considering counters to avoid conflicts.
    """

    # List files in the destination folder.
    folder_files = os.listdir(destination_path)

    # Extract the base name of the file and the extension.
    base_name, extension = os.path.splitext(name)

    # Check if there is a file with the same name (excluding the counter).
    for file_name in folder_files:
        file_base_name, file_extension = os.path.splitext(file_name)

        if base_name == file_base_name:
            # Append '_01' to the existing file name in the folder.
            adjusted_file_name = f'{file_base_name}_01{file_extension}'
            file_name_path = os.path.join(destination_path, file_name)
            adjusted_file_name_path = os.path.join(destination_path, adjusted_file_name)
            os.rename(file_name_path, adjusted_file_name_path)
            # Append '_02' to the name of the file being copied.
            adjusted_name = f'{base_name}_02{extension}'
            return adjusted_name

        if base_name in file_base_name:
            # Increment the max counter by 1 and append to the name of the file being copied.
            existing_files = [f for f in folder_files if f.startswith(base_name)]
            existing_counters = [int(f.split('_')[-1].split('.')[0]) for f in existing_files]
            counter = max(existing_counters, default=1)
            adjusted_name = f'{base_name}_{counter + 1:02d}{extension}'
            return adjusted_name

    # There is no file with the same name.
    return name
