'''Utilities for file hashes'''

# System imports
import functools
import hashlib
import logging
import os


logger = logging.getLogger(__name__)

def check_hash_single(filename: str, checksum_suffix: str = 'sum',
                 read_block_size: int = 1024 * 1024) -> bool:
    """Calculate_and_check_hashes for a single file.

    Args:
        filename (str): _description_
        checksum_suffix (str, optional): _description_. Defaults to 'sum'.
        read_block_size (int, optional): _description_. Defaults to 1024*1024.

    Returns:
        bool: _description_
    """
    hashes = {}

    try:
        sum_filename = f'{filename}.{checksum_suffix}'

        #TODO: Handle the checksum file not existing better.
        with open(sum_filename, 'r', encoding='utf-8') as f_sum:
            for curr_line in f_sum:
                curr_line = curr_line.strip()
                if curr_line.strip() == '':
                    continue

                # Ignore lines begining with '#'
                if curr_line[0] == '#':
                    continue

                parts = curr_line.split(':')
                if len(parts) != 2:
                    logger.error(f"Invalid checksum specification found on line: '{curr_line}'")
                    continue

                curr_algorithm = parts[0].strip().lower()

                if curr_algorithm not in hashlib.algorithms_available:
                    logger.error(f"Sorry but hash algorithm '{curr_algorithm}' is not available")
                    continue

                hashes[curr_algorithm] = {
                    'hash_saved': parts[1].strip().lower(),
                    'hash_calculated': '',
                    'hash_obj': hashlib.new(curr_algorithm),
                }
    except KeyError:
        logger.error(f"Unable to determine checksum file for: {filename}")
        return False
    except FileNotFoundError:
        logger.error(f"Checksum file '{sum_filename}' was not found")
        return False

    with open(filename, 'rb') as f:
        for block in iter(functools.partial(f.read, read_block_size), b''):
            for k,v in hashes.items():
                v['hash_obj'].update(block)

    any_failed_matches = False
    for k,v in hashes.items():
        v['hash_calculated'] = v['hash_obj'].hexdigest()

        # Specifically compare the two hashes, everything should be lower cased
        v['match'] = v['hash_calculated'] == v['hash_saved']

        if v['match'] is False:
            logger.warning(
                f"Hash mis-match found, algo '{k}' calculated "
                f"'{v['hash_calculated']}' should be '{v['hash_saved']}'"
            )
            any_failed_matches = True

    if any_failed_matches:
        return False
    else:
        return True

def create_sum_file(checksum_filename: str, checksums: dict, filesize: int) -> None:
    """Write the checksum data to disk.

    Args:
        checksum_filename (str): _description_
        checksums (dict): _description_
        filesize (int): _description_
    """
    try:
        with open(checksum_filename, 'w', encoding='utf-8') as checksum_file:
            # Write the filesize
            checksum_file.write(f"SIZE : {filesize}\n")
            # Now write the hashes and the values
            for hash_name,hash_data in checksums.items():
                checksum_file.write(
                    f"{hash_name.upper()} : {hash_data['hash_calculated']}\n"
                )
    except Exception as exc:
        logger.error(
            f"Error writing checksum file '{checksum_filename}' - {exc}"
        )
        raise

def calculate_hashes(filename: str,
                    hashes_to_calculate: list[str],
                    read_block_size: int = 1 * 1024 * 1024,
                    ):
    '''Calculate the hashes for the file using the hashes supplied.

    '''

    # Setup the objects for managing the running hashes.
    hashes = {}
    for curr_algorithm in hashes_to_calculate:
        hashes[curr_algorithm] = {
            'hash_calculated': None,
            'hash_obj': hashlib.new(curr_algorithm),
        }

    # Simultaneously hash each block of the file against all the algorithms
    # requested, thus reducing the I/O required.
    # If you are really that interested in performance tuning the block size
    # to ensure a block fits in the CPU cache may be desirable.
    with open(filename, 'rb') as in_file:
        for block in iter(functools.partial(in_file.read, read_block_size), b''):
            for _,hash_data in hashes.items():
                hash_data['hash_obj'].update(block)

    # Save the final hashes to the object for that algorithm.
    for _,hash_data in hashes.items():
        hash_data['hash_calculated'] = hash_data['hash_obj'].hexdigest()

    return hashes

def check_checksum_file(filename: str, suffix: str) -> str:
    '''Generate and check for the existence of the output file.
    '''
    checksum_filename = f"{filename}.{suffix}"

    if os.path.exists(checksum_filename):
        msg = f"Checksum file '{checksum_filename}' already exists"
        # logger.error(msg)
        raise RuntimeError(msg)

    return checksum_filename
