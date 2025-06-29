'''Compression based utilities'''

# System imports
import datetime
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
            'extreme mode': [
                '',
                '-e'
            ]
        }
    },
    # https://web.mit.edu/outland/arch/i386_rhel4/build/p7zip-current/DOCS/MANUAL/switches/method.htm
    '7z': {
        'ext': '7z',
        'extra_args': ['a','-t7z',],
        'params': {
            'compression type': [
                '-m0=lzma2',
                '-m0=lzma',
                '-m0=PPMd',
            ],
            'compression level': [
                '-mx1',
                '-mx5',
                '-mx9',
            ],
        },
        'output': True,
    },
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
            output_fname = f"{filename}.{data['ext']}"
            cli = [cmd]
            cli.extend(data['extra_args'])
            if 'output' in data:
                cli.append(output_fname)
            cli.extend([*cleaned_curr_param_v, filename ])
            # print(f"CLI: {cli}")

            start = datetime.datetime.now()
            result = subprocess.run(cli, capture_output=True)
            end = datetime.datetime.now()

            if result.returncode != 0:
                logger.error(f"Error encoding: {cli}")
                logger.error(f"stdout: {result.stdout}\nstderr: {result.stderr}")


            curr_stat = os.stat(output_fname).st_size
            percentage = (float(curr_stat) / orig_size) * 100
            print(f"| {cmd} | {" , ".join(cleaned_curr_param_v)} | {curr_stat:,} | {percentage:.4f}% | {end - start} |")
            os.remove(output_fname)

    return
