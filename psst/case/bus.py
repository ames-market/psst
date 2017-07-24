import ipywidgets as ipyw
import traitlets as t
import numpy as np
import bqplot as bq
import traittypes as tt

M = 1e10


class Bus(t.HasTraits):

    '''Bus Model'''

    name = t.CUnicode(default_value='GenCo0', help='Name of Generator (str)')
    bus_type = t.Enum(
        values=['SWING', 'PQ', 'PV'],
        default_value='PQ',
        help='Bus type',
    )
    real_power_demand = tt.Array(default_value=[0], minlen=1, help='Active power demand (MW)')
    imag_power_demand = tt.Array(default_value=[0], minlen=1, help='Reactive power demand (MVAR)')
    shunt_conductance = t.CFloat(default_value=0, help='Shunt Conductance (TODO: units)')
    shunt_susceptance = t.CFloat(default_value=0, help='Shunt Susceptance (TODO: units)')
    area = t.CUnicode(default_value='0', help='Area the bus is located in')
    voltage_magnitude = t.CFloat(default_value=1.0, help='Voltage magnitude (p.u.)')
    voltage_angle = t.CFloat(default_value=0.0, help='Voltage angle (deg)')
    base_voltage = t.CFloat(default_value=230, help='Base voltage (kV)')
    zone = t.CUnicode(default_value='0', help='Zone the bus is located in')
    maximum_voltage = t.CFloat(default_value=1.05, help='Maximum voltage')
    minimum_voltage = t.CFloat(default_value=0.95, help='Minimum voltage')

