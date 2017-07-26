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

    g = Generator(
        name='GenCo1',
        generator_bus='Bus1',
        generation_type='NATURALGAS',
        maximum_real_power=100,
        nsegments=3,
    )

    return g

def test_default_generator(default_generator):

    g = default_generator
    assert g.name == 'GenCo1'
    assert g.generator_bus == 'Bus1'
    assert g.generation_type == 'NATURALGAS'

    assert g.maximum_real_power == 100

    assert g.ramp_up_rate == 100
    assert g.ramp_down_rate == 100

    assert len(g.cost_curve_points) == 4
    assert len(g.cost_curve_values) == 4

    with pt.raises(T.TraitError):
        g.ramp_up_rate = 100.5

    with pt.raises(T.TraitError):
        g.ramp_down_rate = 100.5

    assert g.ramp_up_rate == 100
    assert g.ramp_down_rate == 100

    with pt.raises(AttributeError) as excinfo:
        g.ramp_rate

    assert 'ramp_down_rate' in str(excinfo.value) and 'ramp_up_rate' in str(excinfo.value)

    with pt.raises(T.TraitError):
        g.nsegments = 0

    with pt.raises(T.TraitError):
        g.initial_real_power = 100.5

    with pt.raises(T.TraitError):
        g.initial_imag_power = 100.5

    with pt.raises(T.TraitError) as excinfo:
        g.cost_curve_points = [0, 1, 2]

    assert 'must be equal to' in str(excinfo.value)

    with pt.raises(T.TraitError) as excinfo:
        g.cost_curve_values = [0, 1, 2]

    assert 'must be equal to' in str(excinfo.value)


def test_generator_properties(default_generator):

    g = default_generator

    g.ramp_rate = 50

    assert g.ramp_up_rate == 50
    assert g.ramp_down_rate == 50

    assert g.nsegments == 3

    g.nsegments = 10
    assert len(g.cost_curve_points) == 11
    assert len(g.cost_curve_values) == 11

    g.nsegments = 2
    assert len(g.cost_curve_points) == 3
    assert len(g.cost_curve_values) == 3

    g.nsegments = 1
    assert len(g.cost_curve_points) == 2
    assert len(g.cost_curve_values) == 2

    g.maximum_real_power = 200

    assert g.ramp_up_rate == 200
    assert g.ramp_down_rate == 200

    assert g.cost_curve_points[-1] == 200

    g.minimum_real_power = 100

    assert g.cost_curve_points[0] == 100

    g.noload_cost = 5

    for e in g.cost_curve_values:
        assert e == 5

