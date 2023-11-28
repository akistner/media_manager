"""
This script organizes and refactors media files within the input directory.
It processes both image (JPEG) and video (MP4) files.
It gathers metadata to establish a new directory structure and renames files accordingly.

Modules:
- utils: Contains utility functions used in the script.

Dependencies:
- imageio: For obtaining metadata from video files.
- moviepy.editor: For working with video files.
- Pillow: For handling image files and extracting EXIF metadata.
- pywin32: For retrieving media creation time from video files.

Note: Ensure that all dependencies are installed before running the script.

Functions:
- organize_media: Refactors media files in the input directory based on metadata.

Utility Functions:
- get_photo_metadata: Obtains image EXIF metadata.
- get_video_date_time: Obtains the creation time of a video file using propsys and pscon.
- get_video_info: Obtains metadata from a video file using MoviePy and imageio.
- get_video_metadata: Obtains video metadata.
- get_name_date_time: Gets the name date and time of the media file.
- get_media_metadata: Obtains media metadata.
- create_new_name: Creates a new name for the file based on collected dates.
- handle_destination_path: Handles the destination path for a given file based on provided metadata.
- create_new_directory: Copies the media file to a new directory and rename based on metadata.

Status Constants:
- SUCCESS: Indicates a successful operation.
- FAIL: Indicates a failed operation.

Usage:
1. Configure the input and output directories in utils.get_media_directories.
2. Ensure all dependencies are installed by using the 'requirements.txt' file.
3. Run the script.
"""

# Standard.
import copy
import logging
import os
import re
import traceback
from datetime import datetime
from shutil import copyfile
from typing import Optional

# Third-party.
import imageio
from PIL import Image, ExifTags
from moviepy.editor import VideoFileClip
from win32com.propsys import propsys, pscon

# Local.
import utils

# Configures the application's logger.
log_config = {
    'level': logging.ERROR,
    'format': '%(asctime)s [%(levelname)s]: %(message)s',
    'datefmt': '%Y-%m-%d %H:%M:%S',
    'encoding': 'utf-8'
}
logging.basicConfig(**log_config)
logger = logging.getLogger(__name__)

# Status constants for the organize_media function.
SUCCESS = 'SUCCESS'
FAIL = 'FAIL'


def get_photo_metadata(media_path: str, media_metadata: dict) -> dict:
    """
    Obtains image EXIF metadata.

    Args:
        media_path (str): The path to the image file.
        media_metadata (dict): The existing metadata dictionary.

    Returns:
        dict: The updated metadata dictionary with additional EXIF data.
    """

    # Creates a backup copy of the metadata.
    photo_metadata = copy.copy(media_metadata)

    try:
        # Open the image.
        img = Image.open(media_path)

        # Get the image EXIF metadata.
        exif_data = img._getexif()
        if exif_data is not None:
            for tag, value in exif_data.items():
                tag_name = ExifTags.TAGS.get(tag, tag)
                date_format = '%Y:%m:%d %H:%M:%S'
                if tag_name == 'DateTime':
                    date_time = datetime.strptime(value, date_format)
                    photo_metadata['date_time'] = date_time
                elif tag_name == 'DateTimeOriginal':
                    date_time = datetime.strptime(value, date_format)
                    photo_metadata['date_time_original'] = date_time
                elif tag_name == 'DateTimeDigitized':
                    date_time = datetime.strptime(value, date_format)
                    photo_metadata['date_time_digitized'] = date_time

        return photo_metadata

    except Exception as e:
        message = 'Error in the [get_photo_metadata] function. %s'
        logger.error(message, e)
        return media_metadata


def get_video_date_time(media_path: str) -> datetime:
    """
    Obtains the creation time of a video file using propsys and pscon.

    Args:
        media_path (str): The path to the video file.

    Returns:
        datetime: The creation time of the video.
    """
    try:
        properties = propsys.SHGetPropertyStoreFromParsingName(media_path)
        media_encoding_date = pscon.PKEY_Media_DateEncoded
        date_time = properties.GetValue(media_encoding_date)

        if date_time is not None:
            date_time = str(date_time.GetValue())
            date_time = date_time[:-6]
            date_format = "%Y-%m-%d %H:%M:%S"

            try:
                return datetime.strptime(date_time, date_format)
            except ValueError as e:
                message = 'Error in the [get_video_date_time] function. %s'
                logger.error(message, e)

    except Exception as e:
        message = 'Error in the [get_video_date_time] function. %s'
        logger.error(message, e)

    return None


def get_video_info(media_path: str) -> Optional[dict]:
    """
    Obtain metadata from a video file using MoviePy and imageio.

    Args:
        media_path (str): The path to the video file.

    Returns:
        dict: Metadata information of the video.
    """
    try:
        # Open the video using MoviePy.
        vid = VideoFileClip(media_path)

        # Get the video reader using imageio.
        video_reader = imageio.get_reader(media_path)

        # Get metadata from the video.
        metadata = video_reader.get_meta_data()

        # Close the video reader.
        video_reader.close()

        # Close the video.
        vid.close()

        return metadata

    except Exception as e:
        message = 'Error in the [get_video_info] function. %s'
        logger.error(message, e)

    return None


def get_video_metadata(media_path: str, media_metadata: dict) -> dict:
    """
    Obtains video metadata.

    Args:
        media_path (str): The path to the video file.
        media_metadata (dict): The existing metadata dictionary.

    Returns:
        dict: The updated metadata dictionary with additional creation time data.
    """

    # Creates a backup copy of the metadata.
    video_metadata = copy.copy(media_metadata)

    try:
        # Get video creation time using propsys and pscon.
        date_time = get_video_date_time(media_path)
        video_metadata['date_time_created'] = date_time

        # Get media metadata using MoviePy and imageio.
        # info = get_video_info(media_path)
        # video_metadata['info'] = info

        return video_metadata

    except Exception as e:
        message = 'Error in the [get_video_metadata] function. %s'
        logger.error(message, e)
        return media_metadata


def get_name_date_time(media_path: str, media_metadata: dict) -> dict:
    """
    Gets the name date and time of the media file.

    Args:
        media_path (str): The path to the media file.
        media_metadata (dict): The metadata dictionary to update.

    Returns:
        dict: The updated metadata dictionary.
    """

    # Creates a backup copy of the metadata.
    new_metadata = copy.copy(media_metadata)

    try:
        # Get the file name.
        file_name = os.path.basename(media_path)
        file_name = file_name.replace(' ', '')

        # Create regular expression patterns to match the date and time.
        patterns = [
            r'(\d{8})(-)(\d{6})',
            r'(\d{8})(_)(\d{6})',
            r'(\d{4}-\d{2}-\d{2})(at)(\d{2}.\d{2}.\d{2})',
            r'(\d{4}-\d{2}-\d{2})()(\d{2}.\d{2}.\d{2})',
            r'(\d{8})(_)(\d{2}_\d{2}_\d{2})',
            r'(\d{8})(\d{3})',
            r'(\d{8})',
        ]

        # Match the date and time in the file name.
        for pattern in patterns:
            match = re.search(pattern, file_name)

            # If the date and time were found, break the loop.
            if match:
                break

        # If the date and time were not found, raise an exception.
        if not match:
            raise Exception('Could not parse date and time from file name.')

        # To debug.
        # print(f'Pattern match: {match}')

        # Return the date and time.
        if len(match.groups()) == 3:
            date = match.group(1)
            time = match.group(3)
            date = re.sub('[^0-9]', '', date)
            time = re.sub('[^0-9]', '', time)
            date_time = f'{date} {time}'
            date_format = '%Y%m%d %H%M%S'
            date_time = datetime.strptime(date_time, date_format)
            new_metadata['name_date_time'] = date_time
            return new_metadata
        elif len(match.groups()) == 2:
            date = match.group(1)
            date = re.sub('[^0-9]', '', date)
            date = utils.reformat_date(date)
            date = datetime.strptime(date, '%Y%m%d')
            new_metadata['name_date_time'] = date
            return new_metadata
        else:
            date = match.group(1)
            date = re.sub('[^0-9]', '', date)
            date = utils.reformat_date(date)
            date = datetime.strptime(date, '%Y%m%d')
            new_metadata['name_date_time'] = date
            return new_metadata

    except Exception as e:
        message = 'Error in the [get_name_date_time] function. %s'
        logger.error(message, e)
        return media_metadata


def get_media_metadata(media_path: str, media_metadata: dict) -> dict:
    """
    Obtains media metadata.

    Args:
        media_path (str): The path to the media file.
        media_metadata (dict): The metadata dictionary to update.

    Returns:
        dict: The updated metadata dictionary.
    """

    # Creates a backup copy of the metadata.
    new_metadata = copy.copy(media_metadata)

    try:
        # Get the photo or video metadata.
        image_extensions = ['jpg', 'png']
        video_extensions = ['mp4', '3gp']
        if new_metadata['extension'] in image_extensions:
            new_metadata['type'] = 'image'
            new_metadata = get_photo_metadata(media_path, new_metadata)
        elif new_metadata['extension'] in video_extensions:
            new_metadata['type'] = 'video'
            new_metadata = get_video_metadata(media_path, new_metadata)

        # Get the file metadata.
        modification_ts = os.path.getmtime(media_path)
        modification_dt = datetime.fromtimestamp(modification_ts)
        new_metadata['date_time_modified'] = modification_dt

        # Get name date time.
        new_metadata = get_name_date_time(media_path, new_metadata)

        return new_metadata

    except Exception as e:
        message = 'Error in the [get_media_metadata] function processing %s. %s'
        logger.error(message, media_metadata['name'], e)
        return media_metadata


def create_new_name(media_metadata: dict) -> Optional[dict]:
    """
    Creates a new name for the file based on the collected dates.

    Args:
        media_metadata (dict): The metadata dictionary to update.

    Returns:
        dict: The updated metadata dictionary.
    """

    # Creates a backup copy of the metadata.
    new_metadata = copy.copy(media_metadata)

    try:
        # List of keys with datetime values.
        datetime_keys = [
            key for key, value in new_metadata.items() if isinstance(value, datetime)
        ]

        # Find the key with the earliest date.
        earliest_date = min(
            datetime_keys,
            key=lambda k: new_metadata[k] if new_metadata[k].year >= 2000 else datetime.max
        )

        # Check if all dates were earlier than the threshold.
        if new_metadata[earliest_date].year < 2000:
            raise ValueError('No valid dates found for earliest_date.')

        # Get the earliest date.
        earliest_date = new_metadata[earliest_date]
        new_metadata['earliest_date'] = earliest_date

        # Create the prefix.
        prefix = 'img' if new_metadata['type'] == 'image' else 'vid'

        # Removes special characters and inserts prefix.
        formatted_string = str(new_metadata['earliest_date'])
        formatted_string = formatted_string.replace('-', '')
        formatted_string = formatted_string.replace(' ', '_')
        formatted_string = formatted_string.replace(':', '')
        new_name = prefix + '_' + formatted_string

        # Remove the time '00:00:00' from the given file name.
        new_name = utils.remove_time_from_filename(new_name)

        # Get the new name.
        new_metadata['new_name'] = new_name

        return new_metadata

    except Exception as e:
        message = 'Error in the [create_new_name] function. %s'
        logger.error(message, e)
        return media_metadata


def handle_destination_path(file_path: str, output_dir: str, media_metadata: dict) -> str:
    """
    Handles the destination path for a given file based on provided metadata.

    Args:
        file_path (str): The original path of the file.
        output_dir (str): The base directory where the file should be organized.
        media_metadata (dict): Metadata information for the media file.

    Returns:
        str: The new file path after handling based on metadata.

    The function organizes the file into different directories based on metadata.
    If the media file does not have a valid date, it is moved to the 'to_check' directory.
    If the file is a repeated file, it is moved to the 'repeated' directory.
    Otherwise, the file is organized into a regular directory structure based on its date.
    """

    # Get the variables.
    year_dir, month_dir, day_dir, file_name = file_path.split(os.path.sep)[-4:]

    # Check if the media has a valid date.
    if not utils.exist_valid_dates(media_metadata):

        # Create the "to_check" directory.
        to_check_dir = os.path.join(output_dir, 'to_check')
        os.makedirs(to_check_dir, exist_ok=True)

        # Rename the file with a counter if necessary to avoid naming conflicts.
        adjusted_name = utils.handle_counter(media_metadata['name'], to_check_dir)

        # Create the path to copy the file with the adjusted name.
        new_file_path = os.path.join(to_check_dir, adjusted_name)

        # Returns file path in directory "to_check".
        return new_file_path

    if utils.exist_prior_checksum(media_metadata['path'], media_metadata):

        # Create the "repeated" directory.
        repeated_dir = os.path.join(output_dir, 'repeated')
        repeated_dir = os.path.join(repeated_dir, year_dir, month_dir, day_dir)
        os.makedirs(repeated_dir, exist_ok=True)

        # Rename the file with a counter if necessary to avoid naming conflicts.
        adjusted_name = utils.handle_counter(file_name, repeated_dir)

        # Create the path to copy the file with the adjusted name.
        new_file_path = os.path.join(repeated_dir, adjusted_name)

        # Returns file path in directory "repeated".
        return new_file_path

    # Creates regular directory structure.
    regular_dir = os.path.join(output_dir, year_dir, month_dir, day_dir)
    os.makedirs(regular_dir, exist_ok=True)

    # Rename the file with a counter if necessary to avoid naming conflicts.
    adjusted_name = utils.handle_counter(file_name, regular_dir)

    # Create the path to copy the file with the adjusted name.
    new_file_path = os.path.join(regular_dir, adjusted_name)

    # Returns file path in regular directory structure.
    return new_file_path


def create_new_directory(output_dir: str, media_path: str, media_metadata: dict):
    """
    Copies the media file to a new directory structure.
    Renames it based on the provided metadata.

    Args:
        output_dir (str): The path to the output directory.
        media_path (str): The path to the media file.
        media_metadata (dict): The metadata dictionary.

    Raises:
        Exception: If there is an error copying the file.
    """
    try:
        # Extracts date information from the new name.
        date_time = media_metadata['earliest_date']

        # Creates the destination directory path based on the date.
        year_dir = f'{date_time.year}'
        month_dir = f'{date_time.month:02d}'
        day_dir = f'{date_time.day:02d}'
        dest_dir = os.path.join(output_dir, year_dir, month_dir, day_dir)

        # Builds the destination file path.
        new_name = media_metadata['new_name']
        extension = media_metadata['extension']
        new_name = f'{new_name}.{extension}'
        dest_path = os.path.join(dest_dir, new_name)
        dest_path = handle_destination_path(
            dest_path, output_dir, media_metadata)

        # Copies the file to the new directory.
        copyfile(media_path, dest_path)

        # To debug.
        print(f'File moved to: {dest_path}')

    except Exception as e:
        message = 'Error copying the file. %s'
        logger.error(message, e)


def organize_media() -> (str, str):
    """
    Refactors the media files in the input directory.

    Returns:
        tuple: A tuple containing the status of the operation and a message.
    """

    # Paths to the input and output directories.
    input_dir, output_dir = utils.get_media_directories()

    try:
        # Go through all folders and subfolders.
        for root, dirs, files in os.walk(input_dir):

            # Creates dictionary to collect metadata.
            media_metadata = {}

            for media_file in files:

                # Get the file name.
                media_metadata['name'] = media_file

                # To debug.
                print('START')
                print(f'File name: {media_metadata['name']}')

                # Get the file path.
                media_path = os.path.join(root, media_file)
                media_metadata['path'] = media_path

                # Get the file extension.
                file_extension = utils.get_file_extension(media_file)
                media_metadata['extension'] = file_extension

                # Gets the media metadata.
                media_metadata = get_media_metadata(media_path, media_metadata)

                # Name the media.
                media_metadata = create_new_name(media_metadata)

                # Defines the new directory structure.
                create_new_directory(output_dir, media_path, media_metadata)

                # To debug.
                print(f'Metadata:\n{media_metadata}')
                print('END\n')

                # Reset dictionary.
                media_metadata = {}

        return 'SUCCESS', 'Successful media file organization.'

    except Exception as e:
        message = 'Media file organization failed. %s'
        logger.error(message, e)
        return 'FAIL', f'Exception: \n{traceback.format_exc()}'
