from pyomo.environ import *


def build_model(model):

    ####################################################################
    # generator power output at t=0 (initial condition). units are MW. #
    ####################################################################

    model.PowerGeneratedT0 = Var(model.Generators, within=NonNegativeReals)

    ##############################################################################################
    # number of pieces in the linearization of each generator's quadratic cost production curve. #
    ##############################################################################################

    #NL_j Higher the num pieces, better approx -> but harder to solve. Same for all genco offer curves
    model.NumGeneratorCostCurvePieces = Param(within=PositiveIntegers, default=3, mutable=True)

    _build_load(model)
    _build_lines(model)


def _build_load(model):

    #
    # Variables
    #

    # Total demand for reserve requirement
    model.TotalDemand = Var(model.TimePeriods, within=NonNegativeReals)

    def calculate_total_demand(m, t):
        return m.TotalDemand[t] == sum(m.Demand[b,t] for b in m.Buses)

    model.CalculateTotalDemand = Constraint(model.TimePeriods, rule=calculate_total_demand)


def _build_lines(model):
    # amount of power flowing along each line, at each time period

    model.LinePower = Var(model.TransmissionLines, model.TimePeriods, initialize=0)

    def lower_line_power_bounds_rule(m, l, t):
        if m.EnforceLine[l]:
            return -m.ThermalLimit[l] <= m.LinePower[l, t]
        else:
            return Constraint.Skip

    model.LinePowerConstraintLower = Constraint(model.TransmissionLines, model.TimePeriods, rule=lower_line_power_bounds_rule)

    def upper_line_power_bounds_rule(m, l, t):
        if m.EnforceLine[l]:
            return m.ThermalLimit[l] >= m.LinePower[l, t]
        else:
            return Constraint.Skip

    model.LinePowerConstraintHigher = Constraint(model.TransmissionLines, model.TimePeriods, rule=upper_line_power_bounds_rule)


def _build_non_dispatchable(model):

    # assume wind can be curtailed, then wind power is a decision variable
    def nd_bounds_rule(m,n,t):
        return (m.MinNondispatchablePower[n,t], m.MaxNondispatchablePower[n,t])
    model.NondispatchablePowerUsed = Var(model.NondispatchableGenerators, model.TimePeriods, within=NonNegativeReals, bounds=nd_bounds_rule)


def _build_bus(model):
    # voltage angles at the buses (S) (lock the first bus at 0) in radians
    model.Angle = Var(model.Buses, model.TimePeriods, within=Reals, bounds=(-3.14159265,3.14159265))
    def fix_first_angle_rule(m, t):
        return m.Angle[m.Buses[1],t] == 0.0
    model.FixFirstAngle = Constraint(model.TimePeriods, rule=fix_first_angle_rule)


def _build_generators(model):

    # indicator variables for each generator, at each time period.
    model.UnitOn = Var(model.Generators, model.TimePeriods, within=Binary, initialize=1)

    # amount of power produced by each generator, at each time period.
    def power_bounds_rule(m, g, t):
        return (m.MinimumPowerOutput[g], m.MaximumPowerOutput[g])
    model.PowerGenerated = Var(model.Generators, model.TimePeriods, within=NonNegativeReals, bounds=power_bounds_rule)

    # maximum power output for each generator, at each time period.
    model.MaximumPowerAvailable = Var(model.Generators, model.TimePeriods, within=NonNegativeReals)


def _build_cost(model):

    ###################
    # cost components #
    ###################

    # production cost associated with each generator, for each time period.
    model.ProductionCost = Var(model.Generators, model.TimePeriods, within=NonNegativeReals)

    # startup and shutdown costs for each generator, each time period.
    model.StartupCost = Var(model.Generators, model.TimePeriods, within=NonNegativeReals)
    model.ShutdownCost = Var(model.Generators, model.TimePeriods, within=NonNegativeReals)

    # (implicit) binary denoting whether starting up a generator will cost HotStartCost or ColdStartCost
    model.HotStart = Var(model.Generators, model.TimePeriods, bounds=(0,1))


def _build_generation_load(model):

    #####################################################
    # load "shedding" can be both positive and negative #
    #####################################################

    model.LoadGenerateMismatch = Var(model.Buses, model.TimePeriods, within = Reals, initialize=0)
    model.posLoadGenerateMismatch = Var(model.Buses, model.TimePeriods, within = NonNegativeReals, initialize=0)
    model.negLoadGenerateMismatch = Var(model.Buses, model.TimePeriods, within = NonNegativeReals, initialize=0)

    model.GlobalLoadGenerateMismatch = Var(model.TimePeriods, within = Reals, initialize=0)
    model.posGlobalLoadGenerateMismatch = Var(model.TimePeriods, within = NonNegativeReals, initialize=0)
    model.negGlobalLoadGenerateMismatch = Var(model.TimePeriods, within = NonNegativeReals, initialize=0)

    # the following constraints are necessarily, at least in the case of CPLEX 12.4, to prevent
    # the appearance of load generation mismatch component values in the range of *negative* e-5.
    # what these small negative values do is to cause the optimal objective to be a very large negative,
    # due to obviously large penalty values for under or over-generation. JPW would call this a heuristic
    # at this point, but it does seem to work broadly. we tried a single global constraint, across all
    # buses, but that failed to correct the problem, and caused the solve times to explode.

    def pos_load_generate_mismatch_tolerance_rule(m, b):
       return sum((m.posLoadGenerateMismatch[b,t] for t in m.TimePeriods)) >= 0.0
    model.PosLoadGenerateMismatchTolerance = Constraint(model.Buses, rule=pos_load_generate_mismatch_tolerance_rule)

    def neg_load_generate_mismatch_tolerance_rule(m, b):
       return sum((m.negLoadGenerateMismatch[b,t] for t in m.TimePeriods)) >= 0.0
    model.NegLoadGenerateMismatchTolerance = Constraint(model.Buses, rule=neg_load_generate_mismatch_tolerance_rule)


def _build_stage_costs(model):
    pass
    


def _build_miscellaneous(model):

    ##############################
    # Storage decision variables #
    ##############################

    # binary variables for storage (input/output are semicontinuous)
    model.OutputStorage = Var(model.Storage, model.TimePeriods, within=Binary)
    model.InputStorage = Var(model.Storage, model.TimePeriods, within=Binary)

    # amount of output power of each storage unit, at each time period
    def power_output_storage_bounds_rule(m, s, t):
        return (0, m.MaximumPowerOutputStorage[s])
    model.PowerOutputStorage = Var(model.Storage, model.TimePeriods, within=NonNegativeReals, bounds=power_output_storage_bounds_rule)

    # amount of input power of each storage unit, at each time period
    def power_input_storage_bounds_rule(m, s, t):
        return (0, m.MaximumPowerInputStorage[s])
    model.PowerInputStorage = Var(model.Storage, model.TimePeriods, within=NonNegativeReals, bounds=power_input_storage_bounds_rule)

    # state of charge of each storage unit, at each time period
    model.SocStorage = Var(model.Storage, model.TimePeriods, within=PercentFraction)

    #################################################
    # per-stage cost variables - necessary for PySP #
    #################################################

    #
    # Constraints
    #




    # Power balance at each node (S)
    def power_balance(m, b, t):
        # bus b, time t (S)
        return sum((1 - m.GeneratorForcedOutage[g,t]) * m.GeneratorBusContributionFactor[g, b] * m.PowerGenerated[g, t] for g in m.GeneratorsAtBus[b]) \
               + sum(m.PowerOutputStorage[s, t] for s in m.StorageAtBus[b])\
               - sum(m.PowerInputStorage[s, t] for s in m.StorageAtBus[b])\
               + sum(m.NondispatchablePowerUsed[g, t] for g in m.NondispatchableGeneratorsAtBus[b]) \
               + sum(m.LinePower[l,t] for l in m.LinesTo[b]) \
               - sum(m.LinePower[l,t] for l in m.LinesFrom[b]) \
               + m.LoadGenerateMismatch[b,t] \
               == m.Demand[b, t]
    model.PowerBalance = Constraint(model.Buses, model.TimePeriods, rule=power_balance)

    # give meaning to the positive and negative parts of the mismatch
    def posneg_rule(m, b, t):
        return m.posLoadGenerateMismatch[b, t] - m.negLoadGenerateMismatch[b, t] == m.LoadGenerateMismatch[b, t]
    model.Defineposneg_Mismatch = Constraint(model.Buses, model.TimePeriods, rule = posneg_rule)

    def global_posneg_rule(m, t):
        return m.posGlobalLoadGenerateMismatch[t] - m.negGlobalLoadGenerateMismatch[t] == m.GlobalLoadGenerateMismatch[t]
    model.Global_Defineposneg_Mismatch = Constraint(model.TimePeriods, rule = global_posneg_rule)

    # ensure there is sufficient maximal power output available to meet both the
    # demand and the spinning reserve requirements in each time period.
    # encodes Constraint 3 in Carrion and Arroyo.

    model.LoggingCheck26 = BuildCheck(rule=debugger("Enfore reserve requirements rule"))

    def enforce_reserve_requirements_rule(m, t):
        return sum(m.MaximumPowerAvailable[g, t] for g in m.Generators) \
               + sum(m.NondispatchablePowerUsed[n,t] for n in m.NondispatchableGenerators) \
               + sum(m.PowerOutputStorage[s,t] for s in m.Storage) \
                  == \
               m.TotalDemand[t] + m.ReserveRequirement[t] + m.GlobalLoadGenerateMismatch[t]

    model.EnforceReserveRequirements = Constraint(model.TimePeriods, rule=enforce_reserve_requirements_rule)

    # CASM: zonal reserve requirement - ensure there is enough "regulation" reserve
    # in each reserve zone and each time period - This is not an accurate representation or reg up reserves.
    # It will be refined after verification with Alstom. It's just to see if the zonal reserve requirement
    # works.

    model.LoggingCheck27 = BuildCheck(rule=debugger("Create regulating reserve constraints"))


    model.RegulatingReserveUpAvailable = Var(model.Generators, model.TimePeriods, initialize=0.0, within=NonNegativeReals)

    def calculate_regulating_reserve_up_available_per_generator(m, g, t):
        return m.RegulatingReserveUpAvailable[g, t] == m.MaximumPowerAvailable[g,t] - m.PowerGenerated[g,t]
    model.CalculateRegulatingReserveUpPerGenerator = Constraint(model.Generators, model.TimePeriods, rule=calculate_regulating_reserve_up_available_per_generator)

    def enforce_zonal_reserve_requirement_rule(m, rz, t):
        return sum(m.RegulatingReserveUpAvailable[g,t] for g in m.GeneratorsInReserveZone[rz]) >= m.ZonalReserveRequirement[rz, t]

    model.EnforceZonalReserveRequirements = Constraint(model.ReserveZones, model.TimePeriods, rule=enforce_zonal_reserve_requirement_rule)

    ############################################
    # generation limit and ramping constraints #
    ############################################

    # enforce the generator power output limits on a per-period basis.
    # the maximum power available at any given time period is dynamic,
    # bounded from above by the maximum generator output.

    # the following three constraints encode Constraints 16 and 17 defined in Carrion and Arroyo.

    # NOTE: The expression below is what we really want - however, due to a pyomo design feature, we have to split it into two constraints:
    # m.MinimumPowerOutput[g] * m.UnitOn[g, t] <= m.PowerGenerated[g,t] <= m.MaximumPowerAvailable[g, t] <= m.MaximumPowerOutput[g] * m.UnitOn[g, t]

    model.LoggingCheck28 = BuildCheck(rule=debugger("Generator power output constraints"))

    def enforce_generator_output_limits_rule_part_a(m, g, t):
       return m.MinimumPowerOutput[g] * m.UnitOn[g, t] <= m.PowerGenerated[g,t]

    model.EnforceGeneratorOutputLimitsPartA = Constraint(model.Generators, model.TimePeriods, rule=enforce_generator_output_limits_rule_part_a)

    def enforce_generator_output_limits_rule_part_b(m, g, t):
       return m.PowerGenerated[g,t] <= m.MaximumPowerAvailable[g, t]

    model.EnforceGeneratorOutputLimitsPartB = Constraint(model.Generators, model.TimePeriods, rule=enforce_generator_output_limits_rule_part_b)

    def enforce_generator_output_limits_rule_part_c(m, g, t):
       return m.MaximumPowerAvailable[g,t] <= m.MaximumPowerOutput[g] * m.UnitOn[g, t]

    model.EnforceGeneratorOutputLimitsPartC = Constraint(model.Generators, model.TimePeriods, rule=enforce_generator_output_limits_rule_part_c)

    # note: as of 9 Feb 2012 wind is done using Var bounds

    # impose upper bounds on the maximum power available for each generator in each time period,
    # based on standard and start-up ramp limits.

    # the following constraint encodes Constraint 18 defined in Carrion and Arroyo.

    def enforce_max_available_ramp_up_rates_rule(m, g, t):
       # 4 cases, split by (t-1, t) unit status (RHS is defined as the delta from m.PowerGenerated[g, t-1])
       # (0, 0) - unit staying off:   RHS = maximum generator output (degenerate upper bound due to unit being off)
       # (0, 1) - unit switching on:  RHS = startup ramp limit
       # (1, 0) - unit switching off: RHS = standard ramp limit minus startup ramp limit plus maximum power output (degenerate upper bound due to unit off)
       # (1, 1) - unit staying on:    RHS = standard ramp limit plus power generated in previous time period
       if t == 0:
          return m.MaximumPowerAvailable[g, t] <= m.PowerGeneratedT0[g] + \
                                                  m.ScaledNominalRampUpLimit[g] * m.UnitOnT0[g] + \
                                                  m.ScaledStartupRampLimit[g] * (m.UnitOn[g, t] - m.UnitOnT0[g]) + \
                                                  m.MaximumPowerOutput[g] * (1 - m.UnitOn[g, t])
       else:
          return m.MaximumPowerAvailable[g, t] <= m.PowerGenerated[g, t-1] + \
                                                  m.ScaledNominalRampUpLimit[g] * m.UnitOn[g, t-1] + \
                                                  m.ScaledStartupRampLimit[g] * (m.UnitOn[g, t] - m.UnitOn[g, t-1]) + \
                                                  m.MaximumPowerOutput[g] * (1 - m.UnitOn[g, t])

    model.EnforceMaxAvailableRampUpRates = Constraint(model.Generators, model.TimePeriods, rule=enforce_max_available_ramp_up_rates_rule)

    # the following constraint encodes Constraint 19 defined in Carrion and Arroyo.

    def enforce_max_available_ramp_down_rates_rule(m, g, t):
       # 4 cases, split by (t, t+1) unit status
       # (0, 0) - unit staying off:   RHS = 0 (degenerate upper bound)
       # (0, 1) - unit switching on:  RHS = maximum generator output minus shutdown ramp limit (degenerate upper bound) - this is the strangest case.
       # (1, 0) - unit switching off: RHS = shutdown ramp limit
       # (1, 1) - unit staying on:    RHS = maximum generator output (degenerate upper bound)
    #NOTE: As expressed in Carrion-Arroyo and subsequently here, this constraint does NOT consider ramp down from initial conditions to t=1!
       #if t == value(m.NumTimePeriods):
       #   return Constraint.Skip
       #else:
       #   return m.MaximumPowerAvailable[g, t] <= \
       #          m.MaximumPowerOutput[g] * m.UnitOn[g, t+1] + \
       #          m.ScaledShutdownRampLimit[g] * (m.UnitOn[g, t] - m.UnitOn[g, t+1])

       #This version fixes the problem with ignoring initial conditions mentioned in the above note
       if t == 0:
           # Not 100% sure of this one since there is no MaximumPowerAvailableT0
           return m.PowerGeneratedT0[g] <= \
                     m.MaximumPowerOutput[g] * m.UnitOn[g,t] + \
                     m.ScaledShutdownRampLimit[g] * (m.UnitOnT0[g] - m.UnitOn[g,t])
       else:
          return m.MaximumPowerAvailable[g, t-1] <= \
                     m.MaximumPowerOutput[g] * m.UnitOn[g, t] + \
                     m.ScaledShutdownRampLimit[g] * (m.UnitOn[g, t-1] - m.UnitOn[g, t])

    model.EnforceMaxAvailableRampDownRates = Constraint(model.Generators, model.TimePeriods, rule=enforce_max_available_ramp_down_rates_rule)

    # the following constraint encodes Constraint 20 defined in Carrion and Arroyo.

    def enforce_ramp_down_limits_rule(m, g, t):
       # 4 cases, split by (t-1, t) unit status:
       # (0, 0) - unit staying off:   RHS = maximum generator output (degenerate upper bound)
       # (0, 1) - unit switching on:  RHS = standard ramp-down limit minus shutdown ramp limit plus maximum generator output - this is the strangest case.
    #NOTE: This may never be physically true, but if a generator has ScaledShutdownRampLimit >> MaximumPowerOutput, this constraint causes problems
       # (1, 0) - unit switching off: RHS = shutdown ramp limit
       # (1, 1) - unit staying on:    RHS = standard ramp-down limit
       if t == 0:
          return m.PowerGeneratedT0[g] - m.PowerGenerated[g, t] <= \
                 m.ScaledNominalRampDownLimit[g] * m.UnitOn[g, t] + \
                 m.ScaledShutdownRampLimit[g]  * (m.UnitOnT0[g] - m.UnitOn[g, t]) + \
                 m.MaximumPowerOutput[g] * (1 - m.UnitOnT0[g])
       else:
          return m.PowerGenerated[g, t-1] - m.PowerGenerated[g, t] <= \
                 m.ScaledNominalRampDownLimit[g]  * m.UnitOn[g, t] + \
                 m.ScaledShutdownRampLimit[g]  * (m.UnitOn[g, t-1] - m.UnitOn[g, t]) + \
                 m.MaximumPowerOutput[g] * (1 - m.UnitOn[g, t-1])

    model.EnforceScaledNominalRampDownLimits = Constraint(model.Generators, model.TimePeriods, rule=enforce_ramp_down_limits_rule)


    #######################################
    # energy storage bounding constraints #
    #######################################
    # NOTE: The expressions below are what we really want - however, due to a pyomo design feature, we have to split it into two constraints:
    # m.MinimumPowerInputStorage[g] * m.InputStorage[g, t] <= m.StoragePowerInput[g,t] <= m.MaximumPowerInputStorage[g] * m.InputStorage[g, t]
    # m.MinimumPowerOutputStorage[g] * m.OutputStorage[g, t] <= m.StoragePowerOutput[g,t] <= m.MaximumPowerOutputStorage[g] * m.OutputStorage[g, t]

    model.LoggingCheck29 = BuildCheck(rule=debugger("Storage energy constraints"))


    def enforce_storage_input_limits_rule_part_a(m, s, t):
       return m.MinimumPowerInputStorage[s] * m.InputStorage[s, t] <= m.PowerInputStorage[s,t]

    model.EnforceStorageInputLimitsPartA = Constraint(model.Storage, model.TimePeriods, rule=enforce_storage_input_limits_rule_part_a)

    def enforce_storage_input_limits_rule_part_b(m, s, t):
       return m.PowerInputStorage[s,t] <= m.MaximumPowerInputStorage[s] * m.InputStorage[s, t]

    model.EnforceStorageInputLimitsPartB = Constraint(model.Storage, model.TimePeriods, rule=enforce_storage_input_limits_rule_part_b)

    def enforce_storage_output_limits_rule_part_a(m, s, t):
       return m.MinimumPowerOutputStorage[s] * m.OutputStorage[s, t] <= m.PowerOutputStorage[s,t]

    model.EnforceStorageOutputLimitsPartA = Constraint(model.Storage, model.TimePeriods, rule=enforce_storage_output_limits_rule_part_a)

    def enforce_storage_output_limits_rule_part_b(m, s, t):
       return m.PowerOutputStorage[s,t] <= m.MaximumPowerOutputStorage[s] * m.OutputStorage[s, t]

    model.EnforceStorageOutputLimitsPartB = Constraint(model.Storage, model.TimePeriods, rule=enforce_storage_output_limits_rule_part_b)


    def enforce_input_output_exclusivity_rule(m, s, t):
        return m.PowerOutputStorage[s,t] + m.PowerInputStorage[s,t] <= 1

    #model.EnforceInputOutputExclusivity = Constraint(model.Storage, model.TimePeriods, rule=enforce_input_output_exclusivity_rule)

    #####################################
    # energy storage ramping contraints #
    #####################################

    def enforce_ramp_up_rates_power_output_storage_rule(m, s, t):
       if t == 0:
          return m.PowerOutputStorage[s, t] <= m.StoragePowerOutputOnT0[s] + m.ScaledNominalRampUpLimitStorageOutput[s]
       else:
          return m.PowerOutputStorage[s, t] <= m.PowerOutputStorage[s, t-1] + m.ScaledNominalRampUpLimitStorageOutput[s]

    model.EnforceStorageOutputRampUpRates = Constraint(model.Storage, model.TimePeriods, rule=enforce_ramp_up_rates_power_output_storage_rule)

    def enforce_ramp_down_rates_power_output_storage_rule(m, s, t):
       if t == 0:
          return m.PowerOutputStorage[s, t] >= m.StoragePowerOutputOnT0[s] - m.ScaledNominalRampDownLimitStorageOutput[s]
       else:
          return m.PowerOutputStorage[s, t] >= m.PowerOutputStorage[s, t-1] - m.ScaledNominalRampDownLimitStorageOutput[s]

    model.EnforceStorageOutputRampDownRates = Constraint(model.Storage, model.TimePeriods, rule=enforce_ramp_down_rates_power_output_storage_rule)

    def enforce_ramp_up_rates_power_input_storage_rule(m, s, t):
       if t == 0:
          return m.PowerInputStorage[s, t] <= m.StoragePowerInputOnT0[s] + m.ScaledNominalRampUpLimitStorageInput[s]
       else:
          return m.PowerInputStorage[s, t] <= m.PowerInputStorage[s, t-1] + m.ScaledNominalRampUpLimitStorageInput[s]

    model.EnforceStorageInputRampUpRates = Constraint(model.Storage, model.TimePeriods, rule=enforce_ramp_up_rates_power_input_storage_rule)

    def enforce_ramp_down_rates_power_input_storage_rule(m, s, t):
       if t == 0:
          return m.PowerInputStorage[s, t] >= m.StoragePowerInputOnT0[s] - m.ScaledNominalRampDownLimitStorageInput[s]
       else:
          return m.PowerInputStorage[s, t] >= m.PowerInputStorage[s, t-1] - m.ScaledNominalRampDownLimitStorageInput[s]

    model.EnforceStorageInputRampDownRates = Constraint(model.Storage, model.TimePeriods, rule=enforce_ramp_down_rates_power_input_storage_rule)

    ##########################################
    # storage energy conservation constraint #
    ##########################################

    def energy_conservation_rule(m, s, t):
        # storage s, time t
        if t == 0:
            return m.SocStorage[s, t] == m.StorageSocOnT0[s]  + \
                   (- m.PowerOutputStorage[s, t] + m.PowerInputStorage[s,t]*m.EfficiencyEnergyStorage[s])/m.MaximumEnergyStorage[s]
        else:
            return m.SocStorage[s, t] == m.SocStorage[s, t-1]  + \
                   (- m.PowerOutputStorage[s, t] + m.PowerInputStorage[s,t]*m.EfficiencyEnergyStorage[s])/m.MaximumEnergyStorage[s]
    model.EnergyConservation = Constraint(model.Storage, model.TimePeriods, rule=energy_conservation_rule)

    ##################################
    # storage end-point constraints  #
    ##################################

    def storage_end_point_soc_rule(m, s):
        # storage s, last time period
        return m.SocStorage[s, value(m.NumTimePeriods)] == m.EndPointSocStorage[s]
    #model.EnforceEndPointSocStorage = Constraint(model.Storage, rule=storage_end_point_soc_rule)

    #############################################
    # constraints for computing cost components #
    #############################################

    # compute the per-generator, per-time period production costs. this is a "simple" piecewise linear construct.
    # the first argument to piecewise is the index set. the second and third arguments are respectively the input and output variables.
    if config['linearized_cost_curve']:
        model.ComputeProductionCosts = Piecewise(model.Generators * model.TimePeriods, model.ProductionCost, model.PowerGenerated, pw_pts=model.PowerGenerationPiecewisePoints, f_rule=production_cost_function, pw_constr_type='LB')
    else:

        def compute_production_cost_rule(m, g, t):
            return m.ProductionCost[g, t] >= value(m.ProductionCostA0[g]) + value(m.ProductionCostA1[g]) * m.PowerGenerated[g, t] + value(m.ProductionCostA2[g]) * m.PowerGenerated[g, t] * m.PowerGenerated[g, t]

        model.ComputeProductionCosts = Constraint(model.Generators, model.TimePeriods, rule=compute_production_cost_rule)


    # compute the total production costs, across all generators and time periods.
    """def compute_total_production_cost_rule(m):
       return m.TotalProductionCost == sum(m.ProductionCost[g, t] for g in m.Generators for t in m.TimePeriods)

    model.ComputeTotalProductionCost = Constraint(rule=compute_total_production_cost_rule)"""
    ####################################### KICK THAT ONE OUT

    model.LoggingCheck30 = BuildCheck(rule=debugger("Start up and shutdown costs"))

    # compute startup costs for each generator, for each time period
    def compute_hot_start_rule(m, g, t):
        if t <= value(m.ColdStartHours[g]):
            if t - value(m.ColdStartHours[g]) <= value(m.UnitOnT0State[g]):
                m.HotStart[g, t] = 1
                m.HotStart[g, t].fixed = True
                return Constraint.Skip
            else:
                return m.HotStart[g, t] <= sum( m.UnitOn[g, i] for i in range(1, t) )
        else:
            return m.HotStart[g, t] <= sum( m.UnitOn[g, i] for i in range(t - m.ColdStartHours[g], t) )

    model.ComputeHotStart = Constraint(model.Generators, model.TimePeriods, rule=compute_hot_start_rule)

    def compute_startup_costs_rule_minusM(m, g, t):
        if t == 0:
            return m.StartupCost[g, t] >= m.ColdStartCost[g] - (m.ColdStartCost[g] - m.HotStartCost[g])*m.HotStart[g, t] \
                                          - m.ColdStartCost[g]*(1 - (m.UnitOn[g, t] - m.UnitOnT0[g]))
        else:
            return m.StartupCost[g, t] >= m.ColdStartCost[g] - (m.ColdStartCost[g] - m.HotStartCost[g])*m.HotStart[g, t] \
                                          - m.ColdStartCost[g]*(1 - (m.UnitOn[g, t] - m.UnitOn[g, t-1]))

    model.ComputeStartupCostsMinusM = Constraint(model.Generators, model.TimePeriods, rule=compute_startup_costs_rule_minusM)

    # compute the per-generator, per-time period shutdown costs.
    def compute_shutdown_costs_rule(m, g, t):
       if t == 0:
          return m.ShutdownCost[g, t] >= m.ShutdownCostCoefficient[g] * (m.UnitOnT0[g] - m.UnitOn[g, t])
       else:
          return m.ShutdownCost[g, t] >= m.ShutdownCostCoefficient[g] * (m.UnitOn[g, t-1] - m.UnitOn[g, t])

    model.ComputeShutdownCosts = Constraint(model.Generators, model.TimePeriods, rule=compute_shutdown_costs_rule)

    """# compute the total startup and shutdown costs, across all generators and time periods.
    def compute_total_fixed_cost_rule(m):
       return m.TotalFixedCost == sum(m.StartupCost[g, t] + m.ShutdownCost[g, t] for g in m.Generators for t in m.TimePeriods)

    model.ComputeTotalFixedCost = Constraint(rule=compute_total_fixed_cost_rule)"""
    ########################################## KICK THAT OUT ?

    #################################
    # InterfaceConstraint
    #################################

    model.LoggingCheck31 = BuildCheck(rule=debugger("Creating interface power constraints"))


    def interface_rule(m, i, t):
        return sum(m.LinePower[l, t]*m.LinePowerDirectionCoefficient[i, l] for l in m.LinesInInterface[i]) <= m.InterfaceLimit[i]

    model.InterfacePowerConstraint = Constraint(model.Interfaces, model.TimePeriods, rule=interface_rule)


    #######################
    # up-time constraints #
    #######################

    model.LoggingCheck32 = BuildCheck(rule=debugger("Enforce minimum up and down time constraints"))


    # constraint due to initial conditions.
    def enforce_up_time_constraints_initial(m, g):
       if value(m.InitialTimePeriodsOnLine[g]) == 0:
          return Constraint.Skip
       return sum((1 - m.UnitOn[g, t]) for t in m.TimePeriods if t <= value(m.InitialTimePeriodsOnLine[g])) == 0.0

    model.EnforceUpTimeConstraintsInitial = Constraint(model.Generators, rule=enforce_up_time_constraints_initial)

    # constraint for each time period after that not involving the initial condition.
    @simple_constraint_rule
    def enforce_up_time_constraints_subsequent(m, g, t):
       if t <= value(m.InitialTimePeriodsOnLine[g]):
          # handled by the EnforceUpTimeConstraintInitial constraint.
          return Constraint.Skip
       elif t <= (value(m.NumTimePeriods - m.ScaledMinimumUpTime[g]) + 1):
          # the right-hand side terms below are only positive if the unit was off in the previous time period but on in this one =>
          # the value is the minimum number of subsequent consecutive time periods that the unit is required to be on.
          if t == 0:
             return sum(m.UnitOn[g, n] for n in m.TimePeriods if n >= t and n <= (t + value(m.ScaledMinimumUpTime[g]) - 1)) >= \
                    m.ScaledMinimumUpTime[g] * (m.UnitOn[g, t] - m.UnitOnT0[g])
          else:
             return sum(m.UnitOn[g, n] for n in m.TimePeriods if n >= t and n <= (t + value(m.ScaledMinimumUpTime[g]) - 1)) >= \
                    m.ScaledMinimumUpTime[g] * (m.UnitOn[g, t] - m.UnitOn[g, t-1])
       else:
          # handle the final (ScaledMinimumUpTime[g] - 1) time periods - if a unit is started up in
          # this interval, it must remain on-line until the end of the time span.
          if t == 0: # can happen when small time horizons are specified
             return sum((m.UnitOn[g, n] - (m.UnitOn[g, t] - m.UnitOnT0[g])) for n in m.TimePeriods if n >= t) >= 0.0
          else:
             return sum((m.UnitOn[g, n] - (m.UnitOn[g, t] - m.UnitOn[g, t-1])) for n in m.TimePeriods if n >= t) >= 0.0

    model.EnforceUpTimeConstraintsSubsequent = Constraint(model.Generators, model.TimePeriods, rule=enforce_up_time_constraints_subsequent)

    #########################
    # down-time constraints #
    #########################

    # constraint due to initial conditions.
    def enforce_down_time_constraints_initial(m, g):
       if value(m.InitialTimePeriodsOffLine[g]) == 0:
          return Constraint.Skip
       return sum(m.UnitOn[g, t] for t in m.TimePeriods if t <= value(m.InitialTimePeriodsOffLine[g])) == 0.0

    model.EnforceDownTimeConstraintsInitial = Constraint(model.Generators, rule=enforce_down_time_constraints_initial)

    # constraint for each time period after that not involving the initial condition.
    @simple_constraint_rule
    def enforce_down_time_constraints_subsequent(m, g, t):
       if t <= value(m.InitialTimePeriodsOffLine[g]):
          # handled by the EnforceDownTimeConstraintInitial constraint.
          return Constraint.Skip
       elif t <= (value(m.NumTimePeriods - m.ScaledMinimumDownTime[g]) + 1):
          # the right-hand side terms below are only positive if the unit was off in the previous time period but on in this one =>
          # the value is the minimum number of subsequent consecutive time periods that the unit is required to be on.
          if t == 0:
             return sum((1 - m.UnitOn[g, n]) for n in m.TimePeriods if n >= t and n <= (t + value(m.ScaledMinimumDownTime[g]) - 1)) >= \
                    m.ScaledMinimumDownTime[g] * (m.UnitOnT0[g] - m.UnitOn[g, t])
          else:
             return sum((1 - m.UnitOn[g, n]) for n in m.TimePeriods if n >= t and n <= (t + value(m.ScaledMinimumDownTime[g]) - 1)) >= \
                    m.ScaledMinimumDownTime[g] * (m.UnitOn[g, t-1] - m.UnitOn[g, t])
       else:
          # handle the final (ScaledMinimumDownTime[g] - 1) time periods - if a unit is shut down in
          # this interval, it must remain off-line until the end of the time span.
          if t == 0: # can happen when small time horizons are specified
             return sum(((1 - m.UnitOn[g, n]) - (m.UnitOnT0[g] - m.UnitOn[g, t])) for n in m.TimePeriods if n >= t) >= 0.0
          else:
             return sum(((1 - m.UnitOn[g, n]) - (m.UnitOn[g, t-1] - m.UnitOn[g, t])) for n in m.TimePeriods if n >= t) >= 0.0

    model.EnforceDownTimeConstraintsSubsequent = Constraint(model.Generators, model.TimePeriods, rule=enforce_down_time_constraints_subsequent)

    #
    # Cost computations
    #

    def commitment_in_stage_st_cost_rule(m, st):
        return m.CommitmentStageCost[st] == (sum(m.StartupCost[g,t] + m.ShutdownCost[g,t] for g in m.Generators for t in m.CommitmentTimeInStage[st]) + sum(sum(m.UnitOn[g,t] for t in m.CommitmentTimeInStage[st]) * m.MinimumProductionCost[g] * m.TimePeriodLength for g in m.Generators))

    model.Compute_commitment_in_stage_st_cost = Constraint(model.StageSet, rule = commitment_in_stage_st_cost_rule)
    ### NEW COMMITMENT COST RULE
    #

    def generation_in_stage_st_cost_rule(m, st):
        return m.GenerationStageCost[st] == sum(m.ProductionCost[g, t] for g in m.Generators for t in m.GenerationTimeInStage[st]) + m.LoadMismatchPenalty * \
        (sum(m.posLoadGenerateMismatch[b, t] + m.negLoadGenerateMismatch[b, t] for b in m.Buses for t in m.GenerationTimeInStage[st]) + \
                    sum(m.posGlobalLoadGenerateMismatch[t] + m.negGlobalLoadGenerateMismatch[t] for t in m.GenerationTimeInStage[st]))


    model.Compute_generation_in_stage_st_cost = Constraint(model.StageSet, rule = generation_in_stage_st_cost_rule)
    ### NEW GENERATION COST RULE

    def StageCost_rule(m, st):
        return m.StageCost[st] == m.GenerationStageCost[st] + m.CommitmentStageCost[st]
    model.Compute_Stage_Cost = Constraint(model.StageSet, rule = StageCost_rule)

    #
    # Objectives
    #

    model.LoggingCheck33 = BuildCheck(rule=debugger("Create objective function"))


    def total_cost_objective_rule(m):
       return sum(m.StageCost[st] for st in m.StageSet)

    model.TotalCostObjective = Objective(rule=total_cost_objective_rule, sense=minimize)

    # Create a 'dual' suffix component on the instance
    # so the solver plugin will know which suffixes to collect
    # Export and import floating point data
    # model.dual = Suffix(direction=Suffix.IMPORT_EXPORT)
    return model



