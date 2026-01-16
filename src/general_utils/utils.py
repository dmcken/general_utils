'''Utility functions'''

import os


def get_immediate_subdirectories(dir: str) -> list[str]:
    """Get list of directories that are the direct children of the folder specified.

    Args:
        dir (str): _description_

    Returns:
        list[str]: _description_
    """
    return sorted([
        name for name in os.listdir(dir)
            if os.path.isdir(os.path.join(dir, name))
    ])

