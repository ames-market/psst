# Copyright (c) 2020, Battelle Memorial Institute
# Copyright 2007 - present: numerous others credited in AUTHORS.rst

from pyomo.environ import *
import click

def _build_price_sen_load_buses_at_each_zone(m,rz):
    price_sen_load_at_each_zone = []
    for b in m.Buses:
        if b in m.BusesAtEachReserveZone[rz]:
            for l in m.PriceSensitiveLoadsAtBus[b]:
                price_sen_load_at_each_zone.append(l)
    click.echo('zone, price_sen_load_at_each_zone: '+ rz+ str(price_sen_load_at_each_zone))
    return price_sen_load_at_each_zone


def _zone_generator_map(m, g):
    for bus in m.GeneratorsAtBus:
        GenArray = m.GeneratorsAtBus[bus]
        for gen in GenArray:
            if g == gen:
                BusFound = bus
    for zone in m.BusesAtEachReserveZone:
        busArray = m.BusesAtEachReserveZone[zone]
        for bus in busArray:
            if BusFound == bus:
                ZoneFound = zone
    return ZoneFound


def _form_generator_reserve_zones(m,rz):
    ListOfGenCos = []
    for g in m.Generators:
        if m.GenReserveZoneLocation[g]==rz:
            ListOfGenCos.append(g)
    return ListOfGenCos



def _reserve_up_requirement_rule(m, t):
    return m.ReserveUpSystemPercent * max (0, sum(value(m.Demand[b,t]) for b in m.Buses))
def _reserve_down_requirement_rule(m, t):
    return m.ReserveDownSystemPercent * max (0, sum(value(m.Demand[b,t]) for b in m.Buses))

def initialize_global_reserves(model, ReserveDownSystemPercent=None, ReserveUpSystemPercent=None, reserve_up_requirement=_reserve_up_requirement_rule, reserve_down_requirement=_reserve_down_requirement_rule):

    model.ReserveDownSystemPercent = Param(within=Reals, initialize=ReserveDownSystemPercent, mutable=True)
    model.ReserveUpSystemPercent = Param(within=Reals, initialize=ReserveUpSystemPercent, mutable=True)
    model.ReserveUpRequirement = Param(model.TimePeriods, initialize=reserve_up_requirement, within=NonNegativeReals, default=0.0, mutable=True)
    model.ReserveDownRequirement = Param(model.TimePeriods, initialize=reserve_down_requirement, within=NonNegativeReals, default=0.0, mutable=True)


def initialize_regulating_reserves(model):
    model.RegulatingReserveUpAvailable = Var(model.Generators, model.TimePeriods, initialize=0.0, within=NonNegativeReals)

def initialize_zonal_reserves(model, PriceSenLoadFlag=False, zone_names=None, buses_at_each_zone=None, ReserveDownZonalPercent=None, ReserveUpZonalPercent=None, price_sen_load_reserve_zones =_build_price_sen_load_buses_at_each_zone, generator_reserve_zones=_form_generator_reserve_zones, zone_generator_map=_zone_generator_map):

    model.ReserveZones = Set(initialize=zone_names)
    model.BusesAtEachReserveZone = Set(model.ReserveZones, initialize=buses_at_each_zone)

    model.GenReserveZoneLocation = Param(model.Generators, initialize=zone_generator_map)
    model.GeneratorsInReserveZone = Set(model.ReserveZones, initialize=generator_reserve_zones)
    model.DemandInReserveZone = Set(model.ReserveZones, initialize=buses_at_each_zone)

    if PriceSenLoadFlag is True:
        model.PriceSenLoadInReserveZone = Set(model.ReserveZones,initialize=price_sen_load_reserve_zones)

    model.ReserveDownZonalPercent = Param(model.ReserveZones, initialize=ReserveDownZonalPercent, within=NonNegativeReals, default=0.0, mutable=True)
    model.ReserveUpZonalPercent = Param(model.ReserveZones, initialize=ReserveUpZonalPercent, within=NonNegativeReals, default=0.0, mutable=True)
