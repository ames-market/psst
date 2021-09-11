# -*- coding: utf-8 -*-
"""
 Unit test to confirm that PSST can read the bus name strings
 along with setting the bus names as Bus1, Bus 2, ...
 A new df, bus_string, contains the bus names Bus1, Bus 2, ...
 as indices and the bus string
{
    'a';
    'b';
    'c';
};
 as the string name of the bus.  This unit test confirms that
 the indices of the attribute bus_name are identical to that of bus
"""

import psst
from psst.case import read_matpower
import os

CURDIR = os.path.realpath(os.path.dirname(__file__))


def test_bus_name_string():
    matpower_file = os.path.join(CURDIR, "../cases/case3_withbusname.m")
    case = read_matpower(matpower_file)
    # assert case.bus_name.columns == 'BUS_NAME_STRING'


def test_bus_indices():
    matpower_file = os.path.join(CURDIR, "../cases/case3_withbusname.m")
    case = read_matpower(matpower_file)
    assert (case.bus.index == case.bus_name).all()
