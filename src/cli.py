'''CLI functions'''

# System imports
import argparse
import glob
import itertools
import logging
import os
import pprint
import shutil
import subprocess
import sys
import traceback

# Local imports
import general_utils.archive
import general_utils.compression
import general_utils.hashes
import general_utils.utils

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

    available_algos = general_utils.compression.compression_algos.keys()

    parser = argparse.ArgumentParser(
        prog='Compression comparison checks',
        description='Calculate compression values for various algorithms for the specified file.',
    )
    parser.add_argument('filename')
    parser.add_argument(
        '-c','--compression',
        choices=[None,*available_algos],
        default=None,
        help=f"Compression options: {', '.join(available_algos)}"
    )
    # TODO: Add compression algorithm - defaults to all
    args = parser.parse_args()

    return {
        'compression': args.compression,
        'filename': args.filename,
        'tmp': '/dev/shm'
    }

# Compress compare - Start

def compress_compare() -> None:
    """Check compression algorithms.
    """
    config = parse_arguments_compress_compare()
    setup_cli_logging()

    print(f"Params: {config}")

    general_utils.compression.compare_compression(
        config['filename'],
        config['compression'],
    )

    return

# Bulk CBZ - Start

def parse_arguments_bulk_cbz() -> dict[str,str]:
    """Parse arguments for bulk cbz.

    Returns:
        dict[str,str]: configuration parameters.
    """
    parser = argparse.ArgumentParser(
        prog='Bulk cbz',
        description='',
    )
    parser.add_argument('path', type=str, default='.', help="Path to folders to cbz")
    args = parser.parse_args()

    return {
        'path': args.path,
    }

def bulk_cbz() -> None:
    '''Bulk CBZ directories.
    '''
    config = parse_arguments_bulk_cbz()


    '''
    import shutil

    for curr_dir in d:
        general_utils.archive.zipdir(curr_dir,zipFileExtension='cbz')
        shutil.rmtree(curr_dir)
    '''


    dirs_to_cbz = general_utils.utils.get_immediate_subdirectories(config['path'])
    for sub_dir in dirs_to_cbz:
        sub_dir_full_path = os.path.join(
            os.path.abspath(config['path']),
            sub_dir
        )
        sub_dir_entries = os.listdir(sub_dir_full_path)
        invalid_entries = False
        for curr_sub_entry in sub_dir_entries:
            entry_path = os.path.join(sub_dir_full_path, curr_sub_entry)
            if os.path.isdir(entry_path):
                print("Found sub directory")
                invalid_entries = True
                break

            _, f_ext = curr_sub_entry.rsplit('.',maxsplit=1)
            f_ext = f_ext.lower()
            if f_ext not in ['bmp','gif','jpg','jpeg','pdf','png','txt','webp']:
                print(f"Found unwanted file type: {curr_sub_entry}")
                invalid_entries = True
                break

        if invalid_entries:
            print(f"Skipping dir: {sub_dir}")
            continue

        print(f"Dir: '{sub_dir}'", end=' ')
        general_utils.archive.zipdir(sub_dir, file_ext = 'cbz')
        shutil.rmtree(sub_dir_full_path)
        print("Done")

if __name__ == '__main__':
    hash_check()
