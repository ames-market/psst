import ipywidgets as ipyw
import traitlets as t
import numpy as np
import bqplot as bq
import traittypes as tt

M = 1e10


class Branch(t.HasTraits):

    "Branch model"

    name = t.CUnicode(default_value='Branch1', help='Name of Branch (str)')
    from_bus = t.CUnicode(default_value='Bus1', help='Name of From Bus')
    to_bus = t.CUnicode(default_value='Bus2', help='Name of To Bus')
    resistance = t.CFloat(default_value=0, help='Branch resistance (p.u.)')
    reactance = t.CFloat(default_value=0, help='Branch reactance (p.u.)')
    susceptance = t.CFloat(default_value=0, help='Branch susceptance (p.u.)')
    rating = t.CFloat(default_value=M, help='Branch Rating')
    status = t.CBool(default_value=1, help='Branch status')
    angle_minimum = t.CFloat(default_value=0.0, help='Branch angle minimum')
    angle_maximum = t.CFloat(default_value=0.0, help='Branch angle maximum')
    tap = t.CFloat(default_value=None, allow_none=True)
    shift = t.CFloat(default_value=None, allow_none=True)
    from_real_power_flow = t.CFloat(default_value=None, allow_none=True, help='From active power flow (MW)')
    from_imag_power_flow = t.CFloat(default_value=None, allow_none=True, help='From reactive power flow (MVAR)')
    to_real_power_flow = t.CFloat(default_value=None, allow_none=True, help='To active power flow (MW)')
    to_imag_power_flow = t.CFloat(default_value=None, allow_none=True, help='To reactive power flow (MVAR)')

