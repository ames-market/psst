from pyomo.environ import *


def create_interfaces(model, interfaces=None):

	model.Interfaces = Set(initialize=interfaces)

	model.InterfaceFlowLimit = Param(model.Interfaces, 
									within=NonNegativeReals)

	model.LinePowerDirectionCoefficient = Param(model.Interfaces,
											model.TransmissionLines)

	model.LinesInInterfaces = Set(model.Interfaces)

	
