#!/usr/bin/python3
# coding: utf-8

"""
This module is for constants
"""


from enum import Enum


class Service:
    """
    Define all services name
    """
    THSRC = 'THSRC'


class StationMapping(Enum):
    Nangang = 1
    Taipei = 2
    Banqiao = 3
    Taoyuan = 4
    Hsinchu = 5
    Miaoli = 6
    Taichung = 7
    Changhua = 8
    Yunlin = 9
    Chiayi = 10
    Tainan = 11
    Zuouing = 12


class TicketType(Enum):
    ADULT = 'F'
    CHILD = 'H'
    DISABELD = 'W'
    ELDER = 'E'
    COLLEGE = 'P'
