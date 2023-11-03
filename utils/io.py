"""
This module is for I/O.
"""

from __future__ import annotations
import logging
from typing import Union
from pathlib import Path
import rtoml


def load_toml(path: Union[Path, str]) -> dict:
    """Read .toml file"""

    if not isinstance(path, Path):
        path = Path(path)
    if not path.is_file():
        return {}
    return rtoml.load(path)


if __name__:
    logger = logging.getLogger(__name__)
