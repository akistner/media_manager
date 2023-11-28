"""Unit tests for Media Manager project."""

# Standard.
import logging
import os
import datetime

# Local.
import utils
import organizer

# Silence the log.
logging.basicConfig(level=logging.ERROR)
logging.getLogger('utils').setLevel(logging.CRITICAL)
logging.getLogger('organizer').setLevel(logging.CRITICAL)

# Paths to the input and output directories.
input_dir, output_dir = utils.get_media_directories()


def compare_images(file_path_1: str, file_path_2: str) -> bool:
    """
    Compares the checksums (hashes) of two images to determine if they are identical.

    Parameters:
    - file_path_1 (str): The path to the first image file.
    - file_path_2 (str): The path to the second image file.

    Returns:
    - bool: True if the images have identical checksums, False otherwise.
    """

    checksum_1 = utils._calculate_checksum(file_path_1, 'sha3')
    checksum_2 = utils._calculate_checksum(file_path_2, 'sha3')

    return checksum_1 == checksum_2


# ----------------------------------------------------------------
# Starting unit tests.
print('\nSTARTING TESTS\n')

# ----------------------------------------------------------------
# Instantiating variables.
var_1 = os.path.join(input_dir, 'Drives', 'P_20161215_190111_BF.jpg')
var_2 = os.path.join(input_dir, 'Drives', 'P_20161215_190101_BF.jpg')
var_3 = os.path.join(input_dir, 'Drives', 'P_20161215_190101_BF - Copia.jpg')

# Executing the function.
result_1 = compare_images(var_1, var_2)  # False.
result_2 = compare_images(var_1, var_3)  # False.
result_3 = compare_images(var_2, var_3)  # True.

# Checking result.
if not result_1 and not result_2 and result_3:
    print('1. Function "_calculate_checksum": SUCCESS.')
else:
    print('1. Function "_calculate_checksum": FAILED.')

# ----------------------------------------------------------------
# Instantiating variables.
var_1 = {
    'name': '.IMG-20161030-WA0031.jpeg',
    'path': os.path.join(input_dir, 'Drives', '.IMG-20161030-WA0031.jpeg'),
    'extension': 'jpg',
    'type': 'image',
    'date_time': datetime.datetime(2016, 10, 30, 10, 53, 16),
    'date_time_original': datetime.datetime(2016, 10, 30, 10, 53, 16),
    'date_time_digitized': datetime.datetime(2016, 10, 30, 10, 53, 16),
    'date_time_modified': datetime.datetime(2017, 1, 21, 14, 52),
    'name_date_time': datetime.datetime(2016, 10, 30, 0, 0),
    'earliest_date': datetime.datetime(2016, 10, 30, 0, 0),
    'new_name': 'img_20161030_000000'
}
var_2 = {
    'name': '1150332_894445513940472_4820126986969446072_n.jpg',
    'path': os.path.join(input_dir, 'Drives', '1150332_894445513940472_4820126986969446072_n.jpg'),
    'extension': 'jpg',
    'type': 'image',
    'date_time_modified': datetime.datetime(2023, 7, 24, 21, 7, 32),
    'earliest_date': datetime.datetime(2023, 7, 24, 21, 7, 32),
    'new_name': 'img_20230724_210732'
}

# Executing the function.
result_1 = utils.exist_valid_dates(var_1)  # True.
result_2 = utils.exist_valid_dates(var_2)  # False.

# Checking result.
if result_1 and not result_2:
    print('2. Function "exist_valid_dates": SUCCESS.')
else:
    print('2. Function "exist_valid_dates": FAILED.')

# ----------------------------------------------------------------
# Instantiating variables.
var_1 = {
    'name': '.IMG-20161030-WA0031.jpeg',
    'path': os.path.join(input_dir, 'Drives', '.IMG-20161030-WA0031.jpeg'),
    'extension': 'jpg',
    'type': 'image',
    'date_time': datetime.datetime(2016, 10, 30, 10, 53, 16),
    'date_time_original': datetime.datetime(2016, 10, 30, 10, 53, 16),
    'date_time_digitized': datetime.datetime(2016, 10, 30, 10, 53, 16),
    'date_time_modified': datetime.datetime(2017, 1, 21, 14, 52),
    'name_date_time': datetime.datetime(2016, 10, 30, 0, 0),
    'earliest_date': datetime.datetime(2016, 10, 30, 0, 0),
    'new_name': 'img_20161030_000000'
}
var_2 = {
    'name': '1150332_894445513940472_4820126986969446072_n.jpg',
    'path': os.path.join(input_dir, 'Drives', '1150332_894445513940472_4820126986969446072_n.jpg'),
    'extension': 'jpg',
    'type': 'image',
    'date_time_modified': datetime.datetime(2023, 7, 24, 21, 7, 32),
    'earliest_date': datetime.datetime(2023, 7, 24, 21, 7, 32),
    'new_name': 'img_20230724_210732'
}

# Executing the function.
result_1 = utils.exist_prior_checksum(var_1['path'], var_1)  # False.
result_2 = utils.exist_prior_checksum(var_2['path'], var_2)  # False.
result_3 = utils.exist_prior_checksum(var_2['path'], var_2)  # True.

# Checking result.
if not result_1 and not result_2 and result_3:
    print('3. Function "exist_prior_checksum": SUCCESS.')
else:
    print('3. Function "exist_prior_checksum": FAILED.')

# ----------------------------------------------------------------
# Instantiating variables.
var_1 = '15112022.jpg'
var_2 = '20221115.jpg'
var_3 = '20221315.jpg'

# Executing the function.
result_1 = utils.reformat_date(var_1)
result_2 = utils.reformat_date(var_2)
result_3 = utils.reformat_date(var_3)

# Expected outputs.
expected_1 = None
expected_2 = '20221115'
expected_3 = None

# Checking result.
if result_1 is expected_1 and result_2 == expected_2 and result_3 is expected_3:
    print('4. Function "reformat_date": SUCCESS.')
else:
    print('4. Function "reformat_date": FAILED.')

# ----------------------------------------------------------------
# Instantiating variables.
var_1 = 'img_20161030_000000'
var_2 = 'img_20230724_210732'
var_3 = 'img_20230724_000000'

# Executing the function.
result_1 = utils.remove_time_from_filename(var_1)
result_2 = utils.remove_time_from_filename(var_2)
result_3 = utils.remove_time_from_filename(var_3)

# Expected outputs.
expected_1 = 'img_20161030'
expected_2 = 'img_20230724_210732'
expected_3 = 'img_20230724'

# Checking result.
if result_1 == expected_1 and result_2 == expected_2 and result_3 == expected_3:
    print('5. Function "remove_time_from_filename": SUCCESS.')
else:
    print('5. Function "remove_time_from_filename": FAILED.')

# ----------------------------------------------------------------
# Instantiating variables.
var_1 = os.path.join(input_dir, 'Drives', '2013-09-06 16.06.06.jpg')
var_2 = os.path.join(input_dir, 'Drives', 'P_20161215_190101_BF.jpg')
var_3 = os.path.join(input_dir, 'Drives', 'P_20161215_190101_BF - Copia.jpg')
dict_1 = {}
dict_2 = {}
dict_3 = {}

# Executing the function.
result_1 = organizer.get_name_date_time(var_1, dict_1)
result_2 = organizer.get_name_date_time(var_2, dict_2)
result_3 = organizer.get_name_date_time(var_3, dict_3)

# Expected outputs.
expected_1 = {'name_date_time': datetime.datetime(2013, 9, 6, 16, 6, 6)}
expected_2 = {'name_date_time': datetime.datetime(2016, 12, 15, 19, 1, 1)}
expected_3 = {'name_date_time': datetime.datetime(2016, 12, 15, 19, 1, 1)}

# Checking result.
if result_1 == expected_1 and result_2 == expected_2 and result_3 == expected_3:
    print('6. Function "get_name_date_time": SUCCESS.')
else:
    print('6. Function "get_name_date_time": FAILED.')

# ----------------------------------------------------------------
# Ending unit tests.
print('\nEND')
