#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_psst
----------------------------------

Tests for `psst` module.
"""

import numpy as np
import pytest as pt
import traitlets as T

import psst

from psst.case.generator import Generator, GeneratorView, GeneratorCostView

from .test_generator import default_generator

@pt.fixture(scope="module")
def dg():
    return default_generator()

@pt.fixture()
def default_generator_view(dg):

    gv = GeneratorView(
        model=dg
    )

    return gv

@pt.fixture()
def default_generator_cost_view(dg):

    gv = GeneratorCostView(
        model=dg
    )

    return gv

def test_generator_view(default_generator_view):

    gv = default_generator_view
    g = gv.model

    assert isinstance(gv.model, Generator)

    assert gv._title.value == 'Generator:'
    assert gv._name.value == g.name

    assert gv._maximum_real_power.value == gv._initial_real_power.max
    assert gv._maximum_real_power.value == gv._minimum_real_power.max
    assert gv._maximum_real_power.value == gv._ramp_up_rate.max
    assert gv._maximum_real_power.value == gv._ramp_down_rate.max

    assert g.maximum_real_power == gv._maximum_real_power.value
    assert g.name == gv._name.value
    assert g.generation_type == gv._generation_type.value
    assert g.initial_status == gv._initial_status.value
    assert g.minimum_real_power == gv._minimum_real_power.value
    assert g.initial_real_power == gv._initial_real_power.value
    assert g.minimum_up_time == gv._minimum_up_time.value
    assert g.minimum_down_time == gv._minimum_down_time.value
    assert g.nsegments == gv._nsegments.value
    assert g.ramp_up_rate == gv._ramp_up_rate.value
    assert g.ramp_down_rate == gv._ramp_down_rate.value
    assert g.startup_time == gv._startup_time.value
    assert g.shutdown_time == gv._shutdown_time.value
    assert g.noload_cost == gv._noload_cost.value
    assert g.startup_cost == gv._startup_cost.value


def test_generator_costview_generator_view(
        default_generator_cost_view,
        default_generator_view
    ):

    gcv = default_generator_cost_view
    gv = default_generator_view

    assert gv.model == gcv.model

    assert gcv._scale_x.max == gv._maximum_real_power.value

    assert np.all(gcv._scatter.x == gv.model.cost_curve_points)
    assert np.all(gcv._scatter.y == gv.model.cost_curve_values)

    assert np.all(gcv._scatter.x == gcv._lines.x)
    assert np.all(gcv._scatter.y == gcv._lines.y)

    gcv._lines.x = [0, 10, 20, 30]
    gcv._lines.y = [0, 10, 20, 30]

    assert np.all(gcv._scatter.x == gv.model.cost_curve_points)
    assert np.all(gcv._scatter.y == gv.model.cost_curve_values)

    assert np.all(gcv._scatter.x == gcv._lines.x)
    assert np.all(gcv._scatter.y == gcv._lines.y)

