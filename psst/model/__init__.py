import logging

import pandas as pd

from .model import (create_model, initialize_buses,
                initialize_time_periods, initialize_model, Suffix
                    )
from .network import (initialize_network, derive_network, calculate_network_parameters, enforce_thermal_limits)
from .generators import (initialize_generators, initial_state, maximum_minimum_power_output_generators,
                        ramp_up_ramp_down_limits, start_up_shut_down_ramp_limits, minimum_up_minimum_down_time,
                        fuel_cost, piece_wise_linear_cost,
                        production_cost, minimum_production_cost,
                        hot_start_cold_start_costs,
                        forced_outage,
                        generator_bus_contribution_factor)

from .reserves import initialize_global_reserves, initialize_regulating_reserves, initialize_zonal_reserves
from .demand import (initialize_demand)

from .constraints import (constraint_line, constraint_total_demand, constraint_net_power,
                        constraint_load_generation_mismatch,
                        constraint_power_balance,
                        constraint_reserves,
                        constraint_generator_power,
                        constraint_up_down_time,
                        constraint_for_cost,
                        objective_function)

from ..solver import solve_model, PSSTResults
from ..case.utils import calculate_PTDF

logger = logging.getLogger(__file__)


def build_model(case,
                generator_df=None,
                load_df=None,
                branch_df=None,
                bus_df=None,
                previous_unit_commitment_df=None,
                base_MVA=None,
                base_KV=1,
                config=None):

    if base_MVA is None:
        base_MVA = case.baseMVA

    # Configuration
    if config is None:
        config = dict()

    # Get configuration parameters from dictionary
    use_ptdf = config.pop('use_ptdf', False)
    segments = config.pop('segments', 2)
    try:
        reserve_factor = case.reserve_factor
    except AttributeError:
        reserve_factor = config.pop('reserve_factor', 0)

    # Get case data
    generator_df = generator_df or pd.merge(case.gen, case.gencost, left_index=True, right_index=True)
    load_df = load_df or case.load
    branch_df = branch_df or case.branch
    bus_df = bus_df or case.bus

    branch_df.index = branch_df.index.astype(object)
    generator_df.index = generator_df.index.astype(object)
    bus_df.index = bus_df.index.astype(object)
    load_df.index = load_df.index.astype(object)

    branch_df = branch_df.astype(object)
    generator_df = generator_df.astype(object)
    bus_df = bus_df.astype(object)
    load_df = load_df.astype(object)


    # Build model information

    model = create_model()

    initialize_buses(model, bus_names=bus_df.index)
    initialize_time_periods(model, time_periods=list(load_df.index))

    # Build network data
    initialize_network(model, transmission_lines=list(branch_df.index), bus_from=branch_df['F_BUS'].to_dict(), bus_to=branch_df['T_BUS'].to_dict())

    lines_to = {b: list() for b in bus_df.index.unique()}
    lines_from = {b: list() for b in bus_df.index.unique()}

    for i, l in branch_df.iterrows():
        lines_from[l['F_BUS']].append(i)
        lines_to[l['T_BUS']].append(i)

    derive_network(model, lines_from=lines_from, lines_to=lines_to)
    calculate_network_parameters(model, reactance=(branch_df['BR_X'] / base_MVA).to_dict())
    enforce_thermal_limits(model, thermal_limit=branch_df['RATE_A'].to_dict())

    # Build generator data

    generator_at_bus = {b: list() for b in generator_df['GEN_BUS'].unique()}

    for i, g in generator_df.iterrows():
        generator_at_bus[g['GEN_BUS']].append(i)

    initialize_generators(model,
                        generator_names=generator_df.index,
                        generator_at_bus=generator_at_bus)
    fuel_cost(model)

    maximum_minimum_power_output_generators(model,
                                        minimum_power_output=generator_df['PMIN'].to_dict(),
                                        maximum_power_output=generator_df['PMAX'].to_dict())

    ramp_up_ramp_down_limits(model, ramp_up_limits=generator_df['RAMP_10'].to_dict(), ramp_down_limits=generator_df['RAMP_10'].to_dict())

    start_up_shut_down_ramp_limits(model, start_up_ramp_limits=generator_df['STARTUP_RAMP'].to_dict(), shut_down_ramp_limits=generator_df['SHUTDOWN_RAMP'].to_dict())

    minimum_up_minimum_down_time(model, minimum_up_time=generator_df['MINIMUM_UP_TIME'].to_dict(), minimum_down_time=generator_df['MINIMUM_DOWN_TIME'].to_dict())

    forced_outage(model)

    generator_bus_contribution_factor(model)

    if previous_unit_commitment_df is None:
        previous_unit_commitment = dict()
        for g in generator_df.index:
            previous_unit_commitment[g] = [0] * len(load_df)
        previous_unit_commitment_df = pd.DataFrame(previous_unit_commitment)
        previous_unit_commitment_df.index = load_df.index

    diff = previous_unit_commitment_df.diff()

    initial_state_dict = dict()
    for col in diff.columns:
        s = diff[col].dropna()
        diff_s = s[s!=0]
        if diff_s.empty:
            check_row = previous_unit_commitment_df[col].head(1)
        else:
            check_row = diff_s.tail(1)

        if check_row.values == -1 or check_row.values == 0:
            initial_state_dict[col] = -1 * (len(load_df) - int(check_row.index.values))
        else:
            initial_state_dict[col] = len(load_df) - int(check_row.index.values)

    logger.debug("Initial State of generators is {}".format(initial_state_dict))

    initial_state(model, initial_state=initial_state_dict)

    # setup production cost for generators

    points = dict()
    values = dict()

    # TODO : Add segments to config

    for i, g in generator_df.iterrows():
        if g['NCOST'] == 2:
            logger.debug("NCOST=2")
            if g['PMIN'] == g['PMAX']:
                small_increment = 1
            else:
                small_increment = 0
            points[i] = pd.np.linspace(g['PMIN'], g['PMAX'] + small_increment, num=2)
            values[i] = g['COST_0'] + g['COST_1'] * points[i]
        if g['NCOST'] == 3:
            points[i] = pd.np.linspace(g['PMIN'], g['PMAX'], num=segments)
            values[i] = g['COST_0'] + g['COST_1'] * points[i] + g['COST_2'] * points[i] ** 2

    for k, v in points.items():
        points[k] = [float(i) for i in v]
    for k, v in values.items():
        values[k] = [float(i) for i in v]

    piece_wise_linear_cost(model, points, values)

    minimum_production_cost(model)
    production_cost(model)

    # setup start up and shut down costs for generators

    hot_start_costs = case.gencost['STARTUP'].to_dict()
    cold_start_costs = case.gencost['STARTUP'].to_dict()
    shutdown_costs = case.gencost['SHUTDOWN'].to_dict()

    hot_start_cold_start_costs(model, hot_start_costs=hot_start_costs, cold_start_costs=cold_start_costs, shutdown_cost_coefficient=shutdown_costs)

    # Build load data
    load_dict = dict()
    columns = load_df.columns
    for i, t in load_df.iterrows():
        for col in columns:
            load_dict[(col, i)] = t[col]

    initialize_demand(model, demand=load_dict)

    # Initialize Pyomo Variables
    initialize_model(model)

    initialize_global_reserves(model, reserve_factor=reserve_factor)
    initialize_regulating_reserves(model, )
    # initialize_zonal_reserves(model, )

    # impose Pyomo Constraints

    constraint_net_power(model)

    if use_ptdf is True:
        ptdf = calculate_PTDF(case, precision=config.pop('ptdf_precision', None), tolerance=config.pop('ptdf_tolerance', None))
        constraint_line(model, ptdf=ptdf)
    else:
        constraint_line(model, slack_bus=bus_df.index.get_loc(bus_df[bus_df['TYPE'] == 3].index[0])+1)
        # Pyomo is 1-indexed for sets, and MATPOWER type of bus should be used to get the slack bus

    constraint_power_balance(model)

    constraint_total_demand(model)
    constraint_load_generation_mismatch(model)
    constraint_reserves(model)
    constraint_generator_power(model)
    constraint_up_down_time(model)
    constraint_for_cost(model)

    # Add objective function
    objective_function(model)

    for t, row in case.gen_status.iterrows():
        for g, v in row.iteritems():
            if not pd.isnull(v):
                model.UnitOn[g, t].fixed = True
                model.UnitOn[g, t] = int(float(v))

    model.dual = Suffix(direction=Suffix.IMPORT)

    return PSSTModel(model)


class PSSTModel(object):

    def __init__(self, model, is_solved=False):
        self._model = model
        self._is_solved = is_solved
        self._status = None
        self._results = None

    def __repr__(self):

        repr_string = 'status={}'.format(self._status)

        string = '<{}.{}({})>'.format(
                    self.__class__.__module__,
                    self.__class__.__name__,
                    repr_string,)


        return string

    def solve(self, solver='glpk', verbose=False, keepfiles=False, **kwargs):
        solve_model(self._model, solver=solver, verbose=verbose, keepfiles=keepfiles, **kwargs)
        self._results = PSSTResults(self._model)

    @property
    def results(self):
        return self._results
