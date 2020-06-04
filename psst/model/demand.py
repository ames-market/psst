# Copyright (c) 2020, Battelle Memorial Institute
# Copyright 2007 - present: numerous others credited in AUTHORS.rst


from pyomo.environ import *


def initialize_demand(model, demand=None):

    model.Demand = Param(model.Buses, model.TimePeriods, initialize=demand, default=0.0, mutable=True)




