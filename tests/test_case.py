import pytest as pt

import numpy as np
import json
from psst.case.case import Case


@pt.fixture()
def case_default():

    c = Case()

    return c

def test_case_name():

    c = Case(name='case')

    assert repr(c) == "<psst.case.Case(name='case', Generators=2, Buses=2, Branches=1)>"

def test_case(case_default):

    c = case_default

    assert isinstance(c, Case)

    assert list(c.gen.index) == ['GenCo0', 'GenCo1']

    assert c.gen_name == ['GenCo0', 'GenCo1']

    assert c.bus_name == ['Bus1', 'Bus2']

    assert c.swing_bus == 'Bus1'

    assert repr(c) == '<psst.case.Case(Generators=2, Buses=2, Branches=1)>'

def test_case_bus(case_default):

    c = case_default

    np.testing.assert_equal(c.branch.to_dict(), {
        'area': {
            'Bus1': '0',
            'Bus2': '0'
        },
        'base_voltage': {
            'Bus1': 230.0, 'Bus2': 230.0
        },
        'bus_type': {
            'Bus1': 'SWING', 'Bus2': 'PQ'
        },
        'imag_power_demand': {
            'Bus1': array([0]),
            'Bus2': array([0])
        },
        'maximum_voltage': {
            'Bus1': 1.05, 'Bus2': 1.05
        },
        'minimum_voltage': {
            'Bus1': 0.94999999999999996, 'Bus2': 0.94999999999999996
        },
        'real_power_demand': {
            'Bus1': array([50]), 'Bus2': array([250])
        },
        'shunt_conductance': {
            'Bus1': 0.0, 'Bus2': 0.0
        },
        'shunt_susceptance': {
            'Bus1': 0.0, 'Bus2': 0.0
        },
        'voltage_angle': {
            'Bus1': 0.0, 'Bus2': 0.0
        },
        'voltage_magnitude': {
            'Bus1': 1.0, 'Bus2': 1.0
        },
        'zone': {
            'Bus1': '0', 'Bus2': '0'
        }
    })

def test_case_bus(case_default):

    c = case_default

    np.testing.assert_equal(c.bus.to_dict(), {
        "area": {
            "Bus1": "0",
            "Bus2": "0"
        },
        "base_voltage": {
            "Bus1": 230.0,
            "Bus2": 230.0
        },
        "bus_type": {
            "Bus1": "SWING",
            "Bus2": "PQ"
        },
        "imag_power_demand": {
            "Bus1": [
                0
            ],
            "Bus2": [
                0
            ]
        },
        "maximum_voltage": {
            "Bus1": 1.05,
            "Bus2": 1.05
        },
        "minimum_voltage": {
            "Bus1": 0.95,
            "Bus2": 0.95
        },
        "real_power_demand": {
            "Bus1": [
                50
            ],
            "Bus2": [
                250
            ]
        },
        "shunt_conductance": {
            "Bus1": 0.0,
            "Bus2": 0.0
        },
        "shunt_susceptance": {
            "Bus1": 0.0,
            "Bus2": 0.0
        },
        "voltage_angle": {
            "Bus1": 0.0,
            "Bus2": 0.0
        },
        "voltage_magnitude": {
            "Bus1": 1.0,
            "Bus2": 1.0
        },
        "zone": {
            "Bus1": "0",
            "Bus2": "0"
        }
    })

def test_case_generator(case_default):

    c = case_default

    np.testing.assert_equal(c.gen.to_dict(), {
        "base_power": {
            "GenCo0": 100.0,
            "GenCo1": 100.0
        },
        "cost_curve_points": {
            "GenCo0": np.array([
                0.0,
                50.0,
                100.0
            ]),
            "GenCo1": np.array([
                0.0,
                100.0,
                200.0
            ])
        },
        "cost_curve_values": {
            "GenCo0": np.array([
                0,
                0,
                0
            ]),
            "GenCo1": np.array([
                0,
                0,
                0
            ])
        },
        "droop": {
            "GenCo0": None,
            "GenCo1": None
        },
        "generation_type": {
            "GenCo0": "COAL",
            "GenCo1": "COAL"
        },
        "generator_bus": {
            "GenCo0": "Bus1",
            "GenCo1": "Bus2"
        },
        "generator_voltage": {
            "GenCo0": 1.0,
            "GenCo1": 1.0
        },
        "inertia": {
            "GenCo0": None,
            "GenCo1": None
        },
        "initial_imag_power": {
            "GenCo0": 0.0,
            "GenCo1": 0.0
        },
        "initial_real_power": {
            "GenCo0": 0.0,
            "GenCo1": 0.0
        },
        "initial_status": {
            "GenCo0": True,
            "GenCo1": True
        },
        "maximum_imag_power": {
            "GenCo0": 0.0,
            "GenCo1": 0.0
        },
        "maximum_real_power": {
            "GenCo0": 100.0,
            "GenCo1": 200.0
        },
        "minimum_down_time": {
            "GenCo0": 0,
            "GenCo1": 0
        },
        "minimum_imag_power": {
            "GenCo0": 0.0,
            "GenCo1": 0.0
        },
        "minimum_real_power": {
            "GenCo0": 0.0,
            "GenCo1": 0.0
        },
        "minimum_up_time": {
            "GenCo0": 0,
            "GenCo1": 0
        },
        "noload_cost": {
            "GenCo0": 0.0,
            "GenCo1": 0.0
        },
        "nsegments": {
            "GenCo0": 2,
            "GenCo1": 2
        },
        "ramp_down_rate": {
            "GenCo0": 100.0,
            "GenCo1": 200.0
        },
        "ramp_up_rate": {
            "GenCo0": 100.0,
            "GenCo1": 200.0
        },
        "shutdown_time": {
            "GenCo0": 0,
            "GenCo1": 0
        },
        "startup_cost": {
            "GenCo0": 0.0,
            "GenCo1": 0.0
        },
        "startup_time": {
            "GenCo0": 0,
            "GenCo1": 0
        }
    })


def test_unsupported_case():

    with pt.raises(NotImplementedError) as excinfo:
        c = Case(filename='name_of_file.extension')

    assert '.extension' in str(excinfo.value) and 'name_of_file.extension' in str(excinfo.value) and 'please contact the developer' in str(excinfo.value).lower()

