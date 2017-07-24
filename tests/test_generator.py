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


@pt.fixture()
def default_generator():

    g = Generator()

    g.name='GenCo1'
    g.generator_bus='Bus1'
    g.generation_type='NATURALGAS'

    g.maximum_real_power = 100

    with pt.raises(T.TraitError):
        g.ramp_up_rate = 100.5

    with pt.raises(T.TraitError):
        g.ramp_down_rate = 100.5

    assert g.ramp_up_rate == 100
    assert g.ramp_down_rate == 100

    with pt.raises(AttributeError) as excinfo:
        g.ramp_rate

    assert 'ramp_down_rate' in str(excinfo.value) and 'ramp_up_rate' in str(excinfo.value)

    return g


def test_generator_constructor():

    g = Generator(
        name='GenCo1',
        generator_bus='Bus1',
        generation_type='NATURALGAS',
        maximum_real_power=100,
        nsegments=3,
    )

    assert g.ramp_up_rate == 100
    assert g.ramp_down_rate == 100

    assert len(g.cost_curve_points) == 4
    assert len(g.cost_curve_values) == 4

def test_generator_properties(default_generator):

    g = default_generator

    g.ramp_rate = 50

    assert g.ramp_up_rate == 50
    assert g.ramp_down_rate == 50

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
