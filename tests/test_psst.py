#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_psst
----------------------------------

Tests for `psst` module.
"""

import pytest as pt
import traitlets as T

import psst

from psst.case.generator import Generator


def test_generator_input():

    g = Generator()

    g.capacity = 100

    with pt.raises(T.TraitError):
        g.ramp_up_rate = 100.5

    with pt.raises(T.TraitError):
        g.ramp_down_rate = 100.5

    assert g.ramp_up_rate == 0
    assert g.ramp_down_rate == 0

    g.ramp_down_rate = 100
    g.ramp_up_rate = 100

    assert g.ramp_down_rate == 100.0
    assert g.ramp_up_rate == 100.0

    assert g.nsegments == 2

    with pt.raises(T.TraitError):
        g.nsegments = 0

    g.nsegments = 10
    assert len(g.cost_curve_points) == 11
    assert len(g.cost_curve_values) == 11

    g.nsegments = 2
    assert len(g.cost_curve_points) == 3
    assert len(g.cost_curve_values) == 3

    g.nsegments = 1
    assert len(g.cost_curve_points) == 2
    assert len(g.cost_curve_values) == 2
