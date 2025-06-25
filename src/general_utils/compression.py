'''Compression based utilities'''

# System imports
import itertools
import logging
import os
import pprint
import subprocess


# Global definitions
logger = logging.getLogger(__name__)

compression_algos = {
    'bzip2': {
        'ext': 'bz2',
        'extra_args': ['-k'],
        'params': {
            'compression level': [
                '-1',
                '-5',
                '-9',
            ],
        },
    },
    #'gzip': {},
    'xz': {
        'ext': 'xz',
        'extra_args': ['-k'],
        'params': {
            'compression level': [
                '-1',
                '-5',
                '-9',
            ],
            'extreme': [
                '',
                '-e'
            ]
        }
    },
    #'zip': {},
}


def compare_compression(filename: str) -> None:
    """Compare compression algorithms.
    """

    orig_size = os.stat(filename).st_size
    print(f"Original file '{filename} => {orig_size:,}")

    for cmd,data in compression_algos.items():
        logger.info(f"Testing: {cmd} => {pprint.pformat(data['params'])}")

        permutations = list(map(
            lambda x: list(x),
            itertools.product(*data['params'].values())
        ))
        for curr_param_v in permutations:
            # Clean the parameter list
            cleaned_curr_param_v = list(filter(lambda x: x != '', curr_param_v))
            cli = [cmd, *data['extra_args'], *cleaned_curr_param_v, filename ]
            # print(f"CLI: {cli}")

            subprocess.run(cli)

            output_fname = f"{filename}.{data['ext']}"
            curr_stat = os.stat(output_fname).st_size
            percentage = (float(curr_stat) / orig_size) * 100
            print(f"{" , ".join(cleaned_curr_param_v)} => {curr_stat:,} = {percentage:.4f}%")
            os.remove(output_fname)

    return