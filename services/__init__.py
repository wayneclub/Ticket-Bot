#!/usr/bin/python3
# coding: utf-8

"""
This module is for service initiation mapping
"""

from constants import Service
from services.thsrc import THSRC

service_map = [
    {
        'name': Service.THSRC,
        'class': THSRC,
        'keyword': 'thsrc',
    }
]
