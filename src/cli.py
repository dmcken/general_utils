'''CLI functions'''

# System imports
import argparse
import glob
import itertools
import logging
import os
import pprint
import subprocess
import sys
import traceback

# Local imports
import general_utils.compression
import general_utils.hashes

# CLI Functions
logger = logging.getLogger(__name__)

def parse_arguments_create_hashes() -> dict:
    '''Parse arguments and return a config object with appropriate defaults.
    '''
    default_hashes = ['md5','sha1','sha256','sha512']
    default_checksum_suffix = 'sum'

    parser = argparse.ArgumentParser(
        prog='CreateHashes',
        description='Generate hashes for the specified file.',
    )
    parser.add_argument('filename', nargs='+')
    #TODO: add option to specify hashes.
    #TODO: add option to override checksum output filename.
    args = parser.parse_args()

    matched_files = []
    for file in args.filename:
        if glob.escape(file) != file:
            # There are glob pattern chars in the string
            matched_files.extend(glob.glob(file))
        else:
            matched_files.append(file)

    return {
        'hashes': default_hashes,
        'files': matched_files,
        'checksum_suffix': default_checksum_suffix,
    }

def common_args() -> None:
    """Common cli arguments.
    """

def setup_cli_logging() -> None:
    """Common logging setup function.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def hash_create() -> None:
    """Create hashes public CLI interface.
    """
    setup_cli_logging()

    run_data = parse_arguments_create_hashes()

    for curr_file in run_data['files']:
        try:
            logging.info(f"Processing: {curr_file}")
            checksum_filename = general_utils.hashes.check_checksum_file(
                curr_file,
                run_data['checksum_suffix']
            )

            hashes = general_utils.hashes.calculate_hashes(curr_file, run_data['hashes'])
            filesize = os.path.getsize(curr_file)
            general_utils.hashes.create_sum_file(checksum_filename, hashes, filesize)
        # This is a last resort catcher, I want to catch and at least provide some
        # useful information before moving onto the next file.
        # pylint: disable=W0718
        except Exception as exc:
            logging.error(f"Error checksuming file '{curr_file}' - {exc}")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logger.error(pprint.pformat(
                traceback.format_exception(exc_type, exc_value, exc_traceback)
            ))

def hash_check() -> None:
    """Check hashes public CLI interface.
    """
    setup_cli_logging()

    #sw_updates = glob.glob('*.ova')
    sw_updates = glob.glob('*.qcow2')
    #sw_updates = glob.glob('*.tgz')
    #sw_updates = glob.glob('*.vhd')
    for curr_file in sw_updates:
        res = general_utils.hashes.check_hash_single(curr_file)
        logger.info(f"{curr_file:<45} => {res}")


def parse_arguments_compress_compare() -> dict:
    """Parse arguments for compression checks.

    Returns:
        dict: configuration parameters.
    """
    parser = argparse.ArgumentParser(
        prog='Compression checks',
        description='Calculate compression values for various algorithms for the specified file.',
    )
    parser.add_argument('filename')
    args = parser.parse_args()

    return {
        'filename': args.filename,
        'tmp': '/dev/shm'
    }


def compress_compare() -> None:
    """Check compression algorithms.
    """
    config = parse_arguments_compress_compare()
    setup_cli_logging()

    general_utils.compression.compare_compression(config['filename'])

    return


if __name__ == '__main__':
    hash_check()
