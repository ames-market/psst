from pyomo.environ import *


# Not efficient. TODO : Use BuildRule instead
def _generator_bus_rule(m, g):
    for b in m.Buses:
        if g in m.GeneratorsAtBus[b]:
            return b
    print("SERIOUS PROBLEM ENCOUNTERED WHEN INSTANTIATING UC MODEL - NO BUS ASSIGNED TO THERMAL GENERATOR="+str(g))
    return None


def create_generator_bus_relationship(model, 
									generator_bus=_generator_bus_rule):
	

	model.GeneratorBus = Param(model.Generators, 
							within=model.Buses,
							initialize=generator_bus)
	



def _generator_bus_contribution_check(m, g):
    total_contribution = 0
    for b in m.Buses:
        if g in m.GeneratorsAtBus[b]:
            total_contribution += m.GeneratorBusContributionFactor[g, b]
    try:
        np.testing.assert_approx_equal(total_contribution, 1, significant=number_of_significant_digits)
        return True
    except AssertionError as e:
        print(str(e))
        print("\nSum of GeneratorBusContributionFactor for {} is not 1\n".format(g))
        return False


def generator_bus_contribution(model, generator_bus_contribution_factor=1):

	model.GeneratorBusContributionFactor = Param(model.Generators, model.Buses, within=NonNegativeReals, default=1.0)
