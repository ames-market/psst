from pyomo.environ import *

def create_model():
    model = ConcreteModel()
    return model


def initialize_buses(model,
                    bus_names=None,
                    ):

    model.Buses = Set(ordered=True, initialize=bus_names)

def initialize_time_periods(model,
                    time_periods=None
                    ):

    if time_periods is None:
        number_of_time_periods = None
    else:
        number_of_time_periods = len(time_periods)

    model.TimePeriods = Set(initialize=time_periods)
    model.NumTimePeriods = Param(initialize=number_of_time_periods)
    model.TimePeriodLength = Param(default=1.0)

def initialize_model(model,
                    time_period_length=1.0,
                    stage_set=['FirstStage', 'SecondStage'],
                    config=dict()
                    ):

    model.CostCurveType = Param(mutable=True)

    model.StageSet = Set(initialize=stage_set)

    model.CommitmentTimeInStage = Set(model.StageSet,
                                      within=model.TimePeriods,
                                     initialize={'FirstStage': model.TimePeriods,
                                                'SecondStage': list()})

    model.GenerationTimeInStage = Set(model.StageSet,
                                      within=model.TimePeriods,
                                     initialize={'FirstStage': list(),
                                                'SecondStage': model.TimePeriods})

    model.CommitmentStageCost = Var(model.StageSet, within=NonNegativeReals)
    model.GenerationStageCost = Var(model.StageSet, within=NonNegativeReals)

    model.StageCost = Var(model.StageSet, within=NonNegativeReals)

    model.PowerGeneratedT0 = Var(model.Generators, within=NonNegativeReals)

    # indicator variables for each generator, at each time period.
    model.UnitOn = Var(model.Generators, model.TimePeriods, within=Binary, initialize=1)

    # amount of power flowing along each line, at each time period
    model.LinePower = Var(model.TransmissionLines, model.TimePeriods, initialize=0)

    model.NetPowerInjectionAtBus = Var(model.Buses, model.TimePeriods, initialize=0)

    # Demand related variables

    model.TotalDemand = Var(model.TimePeriods, within=NonNegativeReals)

    BigPenalty = config.pop('penalty', 1e6)
    #\Lambda
    model.LoadMismatchPenalty = Param(within=NonNegativeReals, default=BigPenalty)

    # amount of power produced by each generator, at each time period.
    def power_bounds_rule(m, g, t):
        return (0, m.MaximumPowerOutput[g]) 
    model.PowerGenerated = Var(model.Generators, model.TimePeriods, within=NonNegativeReals, bounds=power_bounds_rule)

    # maximum power output for each generator, at each time period.
    model.MaximumPowerAvailable = Var(model.Generators, model.TimePeriods, within=NonNegativeReals)

    # voltage angles at the buses (S) (lock the first bus at 0) in radians
    model.Angle = Var(model.Buses, model.TimePeriods, within=Reals, bounds=(-3.14159265,3.14159265))

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

    #################
    # Load Mismatch #
    #################

    model.LoadGenerateMismatch = Var(model.Buses, model.TimePeriods, within = Reals, initialize=0)
    model.posLoadGenerateMismatch = Var(model.Buses, model.TimePeriods, within = NonNegativeReals, initialize=0)
    model.negLoadGenerateMismatch = Var(model.Buses, model.TimePeriods, within = NonNegativeReals, initialize=0)

    model.GlobalLoadGenerateMismatch = Var(model.TimePeriods, within = Reals, initialize=0)
    model.posGlobalLoadGenerateMismatch = Var(model.TimePeriods, within = NonNegativeReals, initialize=0)
    model.negGlobalLoadGenerateMismatch = Var(model.TimePeriods, within = NonNegativeReals, initialize=0)


