from pyomo.environ import *



def _zone_generator_map(m, g):
    raise NotImplementedError("Zonal reserves not implemented yet")


def _form_generator_reserve_zones(m,rz):
    return (g for g in m.Generators if m.ReserveZoneLocation[g]==rz)


def _reserve_requirement_rule(m, t):
    return m.ReserveFactor * sum(value(m.Demand[b,t]) for b in m.Buses)

def initialize_global_reserves(model, reserve_factor=0.0, reserve_requirement=_reserve_requirement_rule):

    model.ReserveFactor = Param(within=Reals, initialize=reserve_factor, mutable=True)
    model.ReserveRequirement = Param(model.TimePeriods, initialize=reserve_requirement, within=NonNegativeReals, default=0.0, mutable=True)


def initialize_regulating_reserves(model):
    model.RegulatingReserveUpAvailable = Var(model.Generators, model.TimePeriods, initialize=0.0, within=NonNegativeReals)


def initialize_zonal_reserves(model, buses=None, generator_reserve_zones=_form_generator_reserve_zones, zone_generator_map=_zone_generator_map):
    if buses is None:
        buses = model.Buses
    model.ReserveZones = Set(initialize=buses)
    model.ZonalReserveRequirement = Param(model.ReserveZones, model.TimePeriods, default=0.0, mutable=True, within=NonNegativeReals)
    model.ReserveZoneLocation = Param(model.Generators, initialize=zone_generator_map)

    model.GeneratorsInReserveZone = Set(model.ReserveZones, initialize=generator_reserve_zones)

