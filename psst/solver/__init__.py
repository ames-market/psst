# Copyright (c) 2020, Battelle Memorial Institute
# Copyright 2007 - present: numerous others credited in AUTHORS.rst


from pyomo.environ import SolverFactory
import warnings
import os
import click
from .results import PSSTResults
from pyutilib.services import TempfileManager

PSST_WARNING = os.getenv('PSST_WARNING', 'ignore')


def solve_model(model, solver='glpk', solver_io=None, keepfiles=True, verbose=True, symbolic_solver_labels=True, is_mip=True, mipgap=0.01):
    if solver == 'xpress':
        engine = SolverFactory(solver, solver_io=solver_io, is_mip=is_mip)
    else:
        engine = SolverFactory(solver, solver_io=solver_io)
    model.preprocess()
    if is_mip:
        if solver == 'cbc':
            engine.options['ratioGap'] = mipgap
        else:
            engine.options['mipgap'] = mipgap

    with warnings.catch_warnings():
        warnings.simplefilter(PSST_WARNING)
#        TempfileManager.tempdir = os.path.join(os.getcwd(),'PyomoTempFiles')
        resultsPSST = engine.solve(model, suffixes=['dual'], tee=verbose, keepfiles=True, 
                                   symbolic_solver_labels=symbolic_solver_labels)
        TC = str(resultsPSST.solver.termination_condition)

    return model, TC
