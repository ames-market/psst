# -*- coding: utf-8 -*-

import os
import click
import pandas as pd

from .utils import read_unit_commitment, read_model
from .model import build_model

import numpy as np

np.seterr(all='raise')

SOLVER = os.getenv('PSST_SOLVER', 'cbc')


@click.group()
@click.version_option('0.1.0', '--version')
def cli():
    pass


@cli.command()
@click.option('--data', default=None, type=click.Path(), help='Path to model data')
@click.option('--output', default='./xfertoames.dat', type=click.Path(), help='Path to output file')
@click.option('--solver', default=SOLVER, help='Solver')
def scuc(data, output, solver):
    click.echo("Running SCUC using PSST")

    c = read_model(data.strip("'"))
    model = build_model(c)
    model.solve(solver=solver)
    with open(output, 'w') as outfile:

        instance = model._model
        results = {}
        for g in instance.Generators.value:
            for t in instance.TimePeriods:
                results[(g, t)] = instance.UnitOn[g, t]

        for g in sorted(instance.Generators.value):
            outfile.write("%s\n" % str(g).ljust(8))
            for t in sorted(instance.TimePeriods):
                outfile.write("% 1d %6.2f %6.2f\n" % (int(results[(g, t)].value + 0.5), 0.0, 0.0))


@cli.command()
@click.option('--uc', default=None, type=click.Path(), help='Path to unit commitment file')
@click.option('--data', default=None, type=click.Path(), help='Path to model data')
@click.option('--output', default='./output.dat', type=click.Path(), help='Path to output file')
@click.option('--solver', default=SOLVER, help='Solver')
def sced(uc, data, output, solver):

    click.echo("Running SCED using PSST")

    # TODO : Fixme
    uc_df = pd.DataFrame(read_unit_commitment(uc.strip("'")))

    c = read_model(data.strip("'"))
    c.gen_status = uc_df.astype(int)

    model = build_model(c)
    model.solve(solver=solver)

    with open(output.strip("'"), 'w') as f:
        f.write("LMP\n")
        for h, r in model.results.lmp.iterrows():
            bn = 1
            for _, lmp in r.iteritems():
                if lmp is None:
                    lmp = 0
                f.write(str(bn) + ' : ' + str(h + 1) +' : ' + str(lmp) +"\n")
                bn = bn + 1
        f.write("END_LMP\n")

        f.write("GenCoResults\n")
        instance = model._model
        for g in instance.Generators.value:
            f.write("%s\n" % str(g).ljust(8))
            for t in instance.TimePeriods:
                f.write("Hour: {}\n".format(str(t + 1)))
                f.write("\tPowerGenerated: {}\n".format(instance.PowerGenerated[g, t]()))
                f.write("\tProductionCost: {}\n".format(instance.ProductionCost[g, t]()))
                f.write("\tStartupCost: {}\n".format(instance.StartupCost[g, t]()))
                f.write("\tShutdownCost: {}\n".format(instance.ShutdownCost[g, t]()))
        f.write("END_GenCoResults\n")
        f.write("VOLTAGE_ANGLES\n")
        for bus in sorted(instance.Buses):
            for t in instance.TimePeriods:
                f.write('{} {} : {}\n'.format(str(bus), str(t + 1), str(instance.Angle[bus, t]())))
        f.write("END_VOLTAGE_ANGLES\n")
        # Write out the Daily LMP
        f.write("DAILY_BRANCH_LMP\n")
        f.write("END_DAILY_BRANCH_LMP\n")
        # Write out the Daily Price Sensitive Demand
        f.write("DAILY_PRICE_SENSITIVE_DEMAND\n")
        f.write("END_DAILY_PRICE_SENSITIVE_DEMAND\n")
        # Write out which hour has a solution
        f.write("HAS_SOLUTION\n")
        h = 0
        max_hour = 24  # FIXME: Hard-coded number of hours.
        while h < max_hour:
            f.write("1\t")  # FIXME: Hard-coded every hour has a solution.
            h += 1
        f.write("\nEND_HAS_SOLUTION\n")


if __name__ == "__main__":
    cli()
